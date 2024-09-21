import time

# Langchain
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from chromaviz import visualize_collection

from company_data.company import Company

import datetime as dt

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


class ChatBot:
    def __init__(self, ticker: str, use_sec: bool = False) -> None:
        self.ticker = ticker.upper()
        self.company = Company(self.ticker)
        self.use_sec = use_sec

        if self.use_sec:
            self.files_path = self.company.sec_dir
            self.db_path = self.company.sec_db
        else:
            self.files_path = self.company.pdf_dir
            self.db_path = self.company.chroma_path

    def pre_chat_prep(self):
        start = time.time()
        docu = self.load_documnets()
        chunks = self.split_documents(docu)
        # chunks = chunks[4000:]
        self.add_to_chroma(chunks)
        end = time.time()
        elapse = end - start
        elapse = "{:,.2f}".format(elapse / 60)
        print(f"Prep time: {elapse} seconds")

    def load_documnets(self) -> list:
        """
        Load documents in the "docs" folder

        Returns
        -------
        list
            List containing data of PDF files.
        """
        document_loader = PyPDFDirectoryLoader(self.files_path)
        return document_loader.load()

    def split_documents(self, documents: list[Document]):
        """
        Split the document into chunks.

        Parameters
        ----------
        documents : list[Document]
            List containing document file information.

        Returns
        -------
        list
            Split up chunks of the files.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=80,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)

    def get_embedding_function(self):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        return embeddings

    def add_to_chroma(self, chunks: list[Document]):

        # Load the existing database.

        db = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.get_embedding_function(),
        )

        # Calculate Page IDs.
        chunks_with_ids = self.calculate_chunk_ids(chunks)

        # Add or Update the documents.
        existing_items = db.get(include=[])  # IDs are always included by default
        existing_ids = set(existing_items["ids"])
        print(f"Number of existing documents in DB: {len(existing_ids)}")

        # Only add documents that don't exist in the DB.
        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["id"] not in existing_ids:
                new_chunks.append(chunk)

        if len(new_chunks):
            print(f"👉 Adding new documents: {len(new_chunks)}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]

            if len(new_chunks) > 10:

                slice_index = 0
                increment = 10
                while True:
                    try:
                        start = time.time()
                        end_index = slice_index + (increment + 1)
                        sliced_chunk = new_chunks[slice_index:end_index]
                        sliced_ids = new_chunk_ids[slice_index:end_index]
                        db.add_documents(sliced_chunk, ids=sliced_ids)
                        end = time.time()
                        elapse = end - start
                        elapse = "{:,.2f}".format(elapse)
                        print(
                            f"Finished Adding Documents Slices: [Start: {slice_index}, End: {end_index-1}]/{len(new_chunks)}...   [Elapse]: {elapse}  || Finished: {dt.datetime.now().time()}"
                        )
                        slice_index += increment
                    except IndexError:
                        break
                    except KeyboardInterrupt:
                        break

            else:
                db.add_documents(new_chunks, ids=new_chunk_ids)
            print(f"Finished Adding Documents...")
            db.persist()
        else:
            print("✅ No new documents to add")

    def calculate_chunk_ids(self, chunks: list[Document]):
        last_page_id = None
        current_chunk_index = 0
        for chunk in chunks:
            source = chunk.metadata.get("source")
            page = chunk.metadata.get("page")
            current_page_id = f"{source}:{page}"

            # If the page ID is the same as the last one, increment the index.
            if current_page_id == last_page_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0

            # Calculate the chunk ID.
            chunk_id = f"{current_page_id}:{current_chunk_index}"
            last_page_id = current_page_id
            print(f"Chunk: {chunk_id}")
            # Add it to the page meta-data.
            chunk.metadata["id"] = chunk_id

        return chunks

    def query_RAG(self, query_text: str):
        db = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.get_embedding_function(),
        )
        # Search the DB.
        results = db.similarity_search_with_score(query_text, k=5)

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        model = Ollama(model="llama3")
        response_text = model.invoke(prompt)

        sources = [doc.metadata.get("id", None) for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {sources}"

        return response_text, sources

    def handle_chat(self, include_sources: str, use_prep: bool = False):

        if use_prep:
            self.pre_chat_prep()

        print("\n\n-- Starting Chat --\n\n Type 'exit' at any time to quit.\n\n")
        index = 0

        while True:
            user_input = input("\n-----------------------------------\n[User]: ")
            if user_input.lower() == "exit":
                break

            response, sources = self.query_RAG(user_input)

            display = f"\n[ChatBot]: {response}"
            if include_sources:
                display += f"\nSources: {sources}"
            print(display)

    def visualize_knowledge_graph(self, collection_name: str = "langchain"):
        vectordb = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.get_embedding_function(),
        )

        visualize_collection(vectordb._collection)
        # print(f"Collection: {vectordb._collection}")
        # embeddings = collection.get_embeddings()

        # embeddings = embeddings[:1000]

        # visualize_collection(embeddings)
        # # print(f"Collection: {collection}")
        # chroma = Chroma(persist_directory=db_dir)
        # data = chroma.get(collection_name)
        # print(f"Data: {data}")

        # embeddings = data["embeddings"]
        # ids = data["ids"]
        # doc_data = data["data"]

        # print(f"Embeddings: {embeddings}")

        # vector_db = Chroma.from_documents(doc_data, embeddings, ids=ids)

        # collection = chroma.get(collection_name)
        # visualize_collection(collection)

    # collections = chroma.get()

    # visualize_collection(collections)

    def get_valid_collections(self):
        db_dir = f"{self.company.sec_db}"
        chroma = Chroma(persist_directory=db_dir)
        # Get the list of available collections
        collections = chroma._client.list_collections()
        return collections

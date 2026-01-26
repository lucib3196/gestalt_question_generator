from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from pathlib import Path
from typing import Iterator
import pandas as pd


class QuestionModuleDocumentLoader(BaseLoader):
    def __init__(
        self,
        input_col: str,
        output_col: str,
        file_path: (
            str | Path
        ) = r"langgraph_server/src/code_generator/data/QuestionDataV2_06122025_classified.csv",
    ):
        self.file_path = Path(file_path).resolve()
        if not self.file_path.exists():
            raise ValueError(f"Filepath {self.file_path} does not exist")
        self.example_input = input_col
        self.example_output = output_col

    def lazy_load(self) -> Iterator[Document]:
        self.prepare_data()
        for index in self.df.index:
            input_example = self.df.loc[index, self.example_input]
            output_example = self.df.loc[index, self.example_output]

            if pd.isna(input_example):
                continue
            # The page content will be a simple input and output
            content_string = f"""Input Example: {input_example}
                Output Example: {output_example}
                """
            doc_id = f"{Path(self.file_path).stem}:{index}:{self.example_input}->{self.example_output}"
            yield Document(
                id=doc_id,
                page_content=content_string,
                metadata={
                    "source": Path(self.file_path).name,
                    "index": index,
                    "isAdaptive": bool(self.df.loc[index, "isAdaptive"]),
                    "output_is_nan": pd.isna(output_example),
                    "input_col": self.example_input,
                    "output_col": self.example_output,
                },
            )

    def prepare_data(self):
        self.df = self.load_csv()
        # Create a boolean mask where both 'server.js' and 'server.py' are either NaN or empty.
        mask = (self.df["server.js"].isna() | (self.df["server.js"] == "")) & (
            self.df["server.py"].isna() | (self.df["server.py"] == "")
        )
        # This serves as a flag if the file does not contain javascript or python code then
        # The file is assumed to be static
        self.df["is_adaptive"] = (~mask).astype(str)
        return self.df

    def load_csv(self) -> pd.DataFrame:
        self.df = pd.read_csv(self.file_path)
        return self.df

    def validate_csv(self):
        if self.example_input not in self.df.columns:
            raise ValueError(f"Column Name {self.example_input} is not valid")
        if self.example_output not in self.df.columns:
            raise ValueError(f"Column Name {self.example_output} is not valid")


if __name__ == "__main__":
    csv_path = Path(
        r"langgraph_server/src/code_generator/data/QuestionDataV2_06122025_classified.csv"
    ).resolve()
    loader = QuestionModuleDocumentLoader(
        file_path=csv_path, input_col="question", output_col="server.js"
    )
    loader.prepare_data()
    docs = list(loader.lazy_load())
    print(f"Loaded {len(docs)} documents.\n")
    # for doc in docs:
    #     print(type(doc))
    #     print(doc)
    print(docs[0])

import pandas as pd
import json
import zipfile
import tarfile
import os
import io
import warnings
from typing import Union, Dict, Any


class FileProcessor:
    SUPPORTED_FORMATS = {
        "csv",
        "json",
        "h5",
        "parquet",
        "xlsx",
        "zip",
        "tar",
        "gz",
        "bz2",
        "xz",
    }

    @staticmethod
    def process_data(filepath: str) -> Union[pd.DataFrame, Dict, list, bytes]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        file_extension = filepath.rsplit(".", 1)[-1].lower()
        if file_extension not in FileProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_extension}")

        handlers = {
            "csv": pd.read_csv,
            "json": FileProcessor._load_json,
            "h5": pd.read_hdf,
            "parquet": pd.read_parquet,
            "xlsx": pd.read_excel,
            "zip": FileProcessor._process_zip,
            "tar": lambda fp: FileProcessor._process_tar(fp, None),
            "gz": lambda fp: FileProcessor._process_tar(fp, "gz"),
            "bz2": lambda fp: FileProcessor._process_tar(fp, "bz2"),
            "xz": lambda fp: FileProcessor._process_tar(fp, "xz"),
        }

        return handlers[file_extension](filepath)

    @staticmethod
    def _load_json(filepath: str) -> Union[pd.DataFrame, Dict, list]:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if isinstance(data, list) and all(
                    isinstance(item, dict) for item in data
                ):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    return pd.DataFrame.from_dict(data, orient="index")
                return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @staticmethod
    def _process_zip(filepath: str) -> Dict[str, Any]:
        extracted_data = {}
        with zipfile.ZipFile(filepath, "r") as zf:
            for filename in zf.namelist():
                try:
                    with zf.open(filename) as file:
                        data = io.BytesIO(file.read())
                        extracted_data[filename] = FileProcessor.process_data(data)
                except Exception as e:
                    extracted_data[filename] = f"Error processing {filename}: {e}"
                    warnings.warn(f"Error processing {filename}: {e}")
        return extracted_data

    @staticmethod
    def _process_tar(filepath: str, compression: str) -> Dict[str, Any]:
        extracted_data = {}
        mode = f"r:{compression}" if compression else "r"
        with tarfile.open(filepath, mode) as tf:
            for member in tf.getmembers():
                if member.isfile():
                    try:
                        file = tf.extractfile(member)
                        if file:
                            data = io.BytesIO(file.read())
                            extracted_data[member.name] = FileProcessor.process_data(
                                data
                            )
                    except Exception as e:
                        extracted_data[member.name] = (
                            f"Error processing {member.name}: {e}"
                        )
                        warnings.warn(f"Error processing {member.name}: {e}")
        return extracted_data

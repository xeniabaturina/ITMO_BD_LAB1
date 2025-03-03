import configparser
import os
import pandas as pd
from sklearn.model_selection import train_test_split
import traceback

from logger import Logger

TEST_SIZE = 0.3
SHOW_LOG = True


class PenguinPreprocessor:
    """
    Class for preparing penguin dataset for training and testing.
    """

    def __init__(self) -> None:
        logger = Logger(SHOW_LOG)
        self.config = configparser.ConfigParser()
        self.log = logger.get_logger(__name__)
        self.project_path = os.path.join(os.getcwd(), "data")
        self.data_path = os.path.join(self.project_path, "penguins.csv")
        self.X_path = os.path.join(self.project_path, "Penguins_X.csv")
        self.y_path = os.path.join(self.project_path, "Penguins_y.csv")
        self.train_path = [
            os.path.join(self.project_path, "Train_Penguins_X.csv"),
            os.path.join(self.project_path, "Train_Penguins_y.csv"),
        ]
        self.test_path = [
            os.path.join(self.project_path, "Test_Penguins_X.csv"),
            os.path.join(self.project_path, "Test_Penguins_y.csv"),
        ]
        self.log.info("PenguinPreprocessor is ready")

    def get_data(self) -> bool:
        """
        Read raw penguin data and split it into features (X) and target (y).

        Returns:
            bool: True if operation is successful, False otherwise.
        """
        try:
            dataset = pd.read_csv(self.data_path)
            dataset = dataset.dropna()

            X = dataset.drop(["species", "year"], axis=1)
            y = pd.DataFrame(dataset["species"])

            X.to_csv(self.X_path, index=True)
            y.to_csv(self.y_path, index=True)

            if os.path.isfile(self.X_path) and os.path.isfile(self.y_path):
                self.log.info("X and y data is ready")
                self.config["DATA"] = {
                    "X_data": "data/Penguins_X.csv",
                    "y_data": "data/Penguins_y.csv",
                }
                with open("config.ini", "w") as configfile:
                    self.config.write(configfile)
                return True
            else:
                self.log.error("X and y data is not ready")
                return False
        except Exception as e:
            self.log.error(f"Error in get_data: {e}")
            self.log.error(traceback.format_exc())
            return False

    def split_data(self, test_size=TEST_SIZE) -> bool:
        """
        Split the data into training and testing sets.

        Args:
            test_size (float): Proportion of the dataset to include in the test split.

        Returns:
            bool: True if operation is successful, False otherwise.
        """
        try:
            if not os.path.isfile(self.X_path) or not os.path.isfile(self.y_path):
                self.get_data()

            X = pd.read_csv(self.X_path, index_col=0)
            y = pd.read_csv(self.y_path, index_col=0)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )

            self.save_splitted_data(X_train, self.train_path[0])
            self.save_splitted_data(y_train, self.train_path[1])
            self.save_splitted_data(X_test, self.test_path[0])
            self.save_splitted_data(y_test, self.test_path[1])

            self.config["SPLIT_DATA"] = {
                "X_train": "data/Train_Penguins_X.csv",
                "y_train": "data/Train_Penguins_y.csv",
                "X_test": "data/Test_Penguins_X.csv",
                "y_test": "data/Test_Penguins_y.csv",
            }

            self.config["RANDOM_FOREST"] = {
                "n_estimators": "100",
                "max_depth": "None",
                "min_samples_split": "2",
                "min_samples_leaf": "1",
                "path": "experiments/random_forest.sav",
            }

            with open("config.ini", "w") as configfile:
                self.config.write(configfile)

            self.log.info("Data split successfully")
            return True
        except Exception as e:
            self.log.error(f"Error in split_data: {e}")
            self.log.error(traceback.format_exc())
            return False

    def save_splitted_data(self, data, path) -> bool:
        """
        Save the split data to a CSV file.

        Args:
            data (pandas.DataFrame): Data to save.
            path (str): Path to save the data.

        Returns:
            bool: True if operation is successful, False otherwise.
        """
        try:
            data.to_csv(path, index=True)
            if os.path.isfile(path):
                return True
            else:
                self.log.error(f"File {path} is not created")
                return False
        except Exception as e:
            self.log.error(f"Error in save_splitted_data: {e}")
            self.log.error(traceback.format_exc())
            return False


if __name__ == "__main__":
    data_maker = PenguinPreprocessor()
    data_maker.split_data()

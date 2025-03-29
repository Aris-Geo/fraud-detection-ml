import kaggle
from pathlib import Path

def download_fraud_dataset():
    print("Starting the dataset download")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    try:
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            'mlg-ulb/creditcardfraud',
            path=str(data_dir),
            unzip=True
        )
        print(f"Successfully downloaded and extracted dataset to {data_dir.absolute()}")
        
        csv_file = data_dir / "creditcard.csv"
        if csv_file.exists():
            print(f"Found dataset file: {csv_file}")
            print(f"File size: {csv_file.stat().st_size / (1024*1024):.2f} MB")
        else:
            print("Warning: The expected CSV file wasn't found after extraction")
            
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Kaggle API is installed: pip install kaggle")
        print("2. Ensure you've placed your kaggle.json API token in ~/.kaggle/")
        print("3. Check your internet connection")

if __name__ == "__main__":
    download_fraud_dataset()
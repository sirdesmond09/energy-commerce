from azure.storage.blob import BlobServiceClient, BlobBlock
import uuid
import os
import logging
import io

logger = logging.getLogger(__name__)

ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER = os.getenv("AZURE_CONTAINER")


AZURE_STORAGE_ENDPOINT = f"https://{ACCOUNT_NAME}.blob.core.windows.net/"


# def upload(folder, file_name,file):
#     '''
#     Upload large file to azure blob
#     '''
    
#     blob_file_path = f"{folder}/{file_name}"
    
#     try:
#         blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING, timeout=60)
#         blob_client = blob_service_client.get_blob_client(container=CONTAINER, blob=blob_file_path)

#         # upload data
#         block_list=[]
#         chunk_size=1024*1024*4
#         with open(file,'rb') as f:
#             while True:
#                 read_data = f.read(chunk_size)
#                 if not read_data:
#                     break # done
#                 blk_id = str(uuid.uuid4())
#                 blob_client.stage_block(block_id=blk_id,data=read_data) 
#                 block_list.append(BlobBlock(block_id=blk_id))
#         blob_client.commit_block_list(block_list)
#     except Exception as err:
#         logger.exception(str(err))
#         raise err

#     url = AZURE_STORAGE_ENDPOINT + CONTAINER + "/" + blob_client.get_blob_properties().name

#     return url


def upload(folder, file_name, file):
    '''
    Upload large file to Azure Blob
    '''
    
    blob_file_path = f"{folder}/{file_name}"
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING, timeout=60)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER, blob=blob_file_path)

        # Upload data
        block_list = []
        chunk_size = 1024 * 1024 * 4
        
        with io.BytesIO() as f:
            for chunk in file.chunks():
                f.write(chunk)
            f.seek(0)
            
            while True:
                read_data = f.read(chunk_size)
                if not read_data:
                    break  # Done
                blk_id = str(uuid.uuid4())
                blob_client.stage_block(block_id=blk_id, data=read_data) 
                block_list.append(BlobBlock(block_id=blk_id))
        
        blob_client.commit_block_list(block_list)
    except Exception as err:
        logger.exception(str(err))
        raise err

    url = AZURE_STORAGE_ENDPOINT + CONTAINER + "/" + blob_client.get_blob_properties().name

    return url
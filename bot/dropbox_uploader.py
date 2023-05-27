""" Dropbox uploader module """
from typing import Optional

import dropbox
from dropbox.exceptions import ApiError, AuthError


class DropboxUploader:
    """Dropbox uploader class"""

    def __init__(self, access_token):
        self.dbx = dropbox.Dropbox(access_token)
        self.path_to_upload = "/destination"

    def upload_file_to_dropbox(
        self, data_to_upload: bytes, target_path: str
    ) -> Optional[str]:
        """upload file to dropbox
        Args:
            data_to_upload (bytes): data to upload to dropbox
            target_path (str): target path to upload
        Returns:
            Optional[str]: temporary link to download file
        """
        try:
            target_path = f"{self.path_to_upload}/{target_path}"
            self.dbx.files_upload(data_to_upload, target_path)
            temporary_1_minute_link = self.dbx.files_get_temporary_link(target_path)
            if temporary_1_minute_link:
                return temporary_1_minute_link.link

        except AuthError as error:
            print(f"Error authenticating Dropbox API: {error}")
        except ApiError as error:
            print(f"API error occurred while uploading file: {error}")
        return None

    def list_files_in_dropbox_folder(self) -> Optional[list]:
        """list files in dropbox folder
        Returns:
            Optional[list]: list of files in dropbox folder
        """

        try:
            files = self.dbx.files_list_folder(self.path_to_upload)
            if files:
                return files.entries
        except AuthError as error:
            print(f"Error authenticating Dropbox API: {error}")
        except ApiError as error:
            print(f"API error occurred while listing files in folder: {error}")
        return []

    def remove_file_from_dropbox(self, file_path: str):
        """remove file from dropbox

        Args:
            file_path (str): path to file to remove
        """
        try:
            self.dbx.files_delete(file_path)
        except AuthError as error:
            print(f"Error authenticating Dropbox API: {error}")
        except ApiError as error:
            print(f"API error occurred while removing file: {error}")

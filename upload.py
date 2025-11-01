#!/usr/bin/env python3
import argparse
import json
import logging
import os
import os.path as path
import re
from plugins import TEXT
from creds import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_TOKEN_FILE
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

logger = logging.getLogger(__name__)

FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
drive: GoogleDrive
http = None
initial_folder = None
TOKEN_FILE_PATH = GOOGLE_TOKEN_FILE


def ensure_token_storage() -> None:
    token_dir = os.path.dirname(TOKEN_FILE_PATH)
    if token_dir and not os.path.exists(token_dir):
        os.makedirs(token_dir, exist_ok=True)


def upload(filename: str, update, context, parent_folder: str = None) -> None:

    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
    drive: GoogleDrive
    http = None
    initial_folder = None
    gauth: drive.GoogleAuth = GoogleAuth()
    ensure_token_storage()
    gauth.LoadCredentialsFile(TOKEN_FILE_PATH)

    if gauth.credentials is None:
        logger.warning("⚠️ 尚未完成授权流程。")
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
        ensure_token_storage()
        gauth.SaveCredentialsFile(TOKEN_FILE_PATH)
    else:
        # Initialize the saved creds
        gauth.Authorize()
    drive = GoogleDrive(gauth)
    http = drive.auth.Get_Http_Object()
    if not path.exists(filename):
        logger.error("❌ 指定的文件不存在：%s", filename)
        return
    # print(filename)
    
    default_folder_id = GOOGLE_DRIVE_FOLDER_ID

    if not default_folder_id:

        if parent_folder:

                # Check the files and folers in the root foled
                file_list = drive.ListFile(
                    {'q': "'root' in parents and trashed=false"}).GetList()
                for file_folder in file_list:
                    if file_folder['title'] == parent_folder:
                        # Get the matching folder id
                        folderid = file_folder['id']
                        # print(folderid)
                        logger.info("📂 云端已存在目标文件夹，直接使用。")
                        # We need to leave this if it's done
                        break
                else:
                    # Create folder
                    folder_metadata = {'title': parent_folder,
                                       'mimeType': 'application/vnd.google-apps.folder'}
                    folder = drive.CreateFile(folder_metadata)
                    folder.Upload()
                    folderid = folder['id']
                    # Get folder info and print to screen
                    foldertitle = folder['title']
                    # folderid = folder['id']
                    logger.info("📂 已创建新的云端文件夹：%s (ID: %s)", foldertitle, folderid)

    file_params = {'title': filename.split('/')[-1]}
    
    if default_folder_id:
        file_params['parents'] = [{"kind": "drive#fileLink", "id": default_folder_id}]
    else:
        if parent_folder:
            file_params['parents'] = [{"kind": "drive#fileLink", "id": folderid}]
        
    file_to_upload = drive.CreateFile(file_params)
    file_to_upload.SetContentFile(filename)
    try:
        upload_params = {"http": http}
        if default_folder_id:
            upload_params["supportsTeamDrives"] = True
        file_to_upload.Upload(param=upload_params)
        
        
    except Exception as e:
        logger.error("❌ 上传文件时出错：%s", e)
    if not default_folder_id:
        file_to_upload.FetchMetadata()
        file_to_upload.InsertPermission({
        'type':  'anyone', 'value': 'anyone', 'role':  'reader', 'withLink': True
    })
        
    return file_to_upload['webContentLink']

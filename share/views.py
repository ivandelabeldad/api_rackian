import os
import random
import shutil

from django.http import HttpResponse
from rest_framework import viewsets, mixins, views
from rest_framework import authentication, permissions
from rest_framework.response import Response
from storage.models import Folder

from api_rackian.settings import STORAGE_FOLDER_ABS
from storage.models import File
from . import serializers, models


class PermissionViewset(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = serializers.PermissionSerializer
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return models.Permission.objects.all()


class FileLinkViewset(viewsets.ModelViewSet):
    serializer_class = serializers.FileLinkSerializer
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        file_links = models.FileLink.objects.all()
        file_filter = self.request.query_params.get('file', None)
        if file_filter is not None:
            if file_filter != '':
                file_links = file_links.filter(file=file_filter)
        return file_links


class FolderLinkViewset(viewsets.ModelViewSet):
    serializer_class = serializers.FolderLinkSerializer
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return models.FolderLink.objects.all()


class ShareFileView(views.APIView):
    """
    A View for download Files.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        """
        Download file.
        """
        try:
            filelink = models.FileLink.objects.filter(id=id).first()
            return ShareFileView.download_file(filelink.file)
        except:
            return Response('not exists', 404)

    @staticmethod
    def download_file(file):
        file_location = ''.join((STORAGE_FOLDER_ABS, '/', file.id))
        fp = open(file_location, 'rb')
        response = HttpResponse(fp.read(), content_type=file.mime_type)
        response['Content-Length'] = fp.tell()

        # ALLOW SEE FILENAME
        response['filename'] = file.name + file.extension
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-Custom-header'
        response['Access-Control-Expose-Headers'] = 'filename'



        fp.close()
        response['Content-Disposition'] = 'inline; filename=' + file.name + file.extension
        return response


class ShareFolderView(views.APIView):
    """
    A View for download Files.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        """
        Download folder.
        """
        try:
            folderlink = models.FolderLink.objects.filter(id=id).first()
            return ShareFolderView.download_folder(folderlink.folder)
        except:
            return Response('not exists', 404)

    @staticmethod
    def download_folder(folder):
        tmp_folder = ''.join(('./tmp-', folder.id, '-', str(random.randint(1000, 9999))))
        root_folder = ''.join((tmp_folder, '/', folder.name))
        os.mkdir(tmp_folder)
        try:
            ShareFolderView.generate_folder(tmp_folder, folder)
            shutil.make_archive(root_folder, 'zip', tmp_folder)
            fp = open(''.join((root_folder, '.zip')), 'rb')
            response = HttpResponse(fp.read(), content_type='application/zip')
            response['Content-Length'] = fp.tell()
            fp.close()
            response['Content-Disposition'] = 'inline; filename=' + folder.name + '.zip'
            shutil.rmtree(tmp_folder)
            return response
        except:
            shutil.rmtree(tmp_folder)
            raise

    @staticmethod
    def generate_folder(folder_path, folder, shutil=None):
        if not folder:
            return
        new_folder = ''.join((folder_path, '/', folder.name))
        os.mkdir(new_folder)
        files = File.objects.filter(folder=folder.id).all()
        for file in files:
            file_name = file.name
            origin = ''.join((STORAGE_FOLDER_ABS, '/', file.id))
            dest = ''.join((new_folder, '/', file_name, file.extension))
            number = 1
            while os.path.isfile(dest):
                file_name = ''.join((file.name, ' (', str(number), ')'))
                dest = ''.join((new_folder, '/', file_name, file.extension))
                number += 1
            shutil.copy2(origin, dest)
        folders = Folder.objects.filter(parent_folder=folder.id).all()
        for f in folders:
            ShareFolderView.generate_folder(new_folder, f)

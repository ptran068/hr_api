#!/usr/bin/env python

# author Huy 
# date 11/30/2019

from rest_framework import viewsets


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {}

    def get_permissions(self):
        return [permission() for permission in self.permission_classes_by_action.get(self.action, self.permission_classes)]

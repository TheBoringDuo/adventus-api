from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS

class CanAddBusinessObjects(BasePermission):
	def has_permission(self, request, view):
		if request.user.is_authenticated:
			if request.user.isBusinessClient or request.user.is_superuser:
				return True
		return False

	def has_object_permission(self, request, view, obj):
		return True


class CanEditBusinessObject(BasePermission):
	def has_permission(self, request, view):
		if request.user.is_authenticated:
			if request.user.isBusinessClient or request.user.is_superuser:
				return True
		return False

	def has_object_permission(self, request, view, businessObj):
		if businessObj.ownedBy.id == request.user.id and businessObj.active:
			return True
		return False



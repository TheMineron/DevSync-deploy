from django.contrib.auth.models import AbstractUser

from config import settings
from notifications.models import Notification
from notifications.services.action_building import TemplateActionsBuilder
from notifications.services.factories import TemplateNotificationFactory
from notifications.services.services import NotificationService, NotificationContextServiceBase, \
    NotificationServiceBase
from notifications.services.template_loading import NotificationTemplateLoader
from notifications.services.utils import update_notification_footer
from projects.exceptions import ProjectInvitationIsExpiredError
from projects.models import ProjectInvitation


class ProjectInvitationNotificationService(NotificationService[ProjectInvitation]):
    def __init__(
            self,
            template_name: str,
            template_loader: NotificationTemplateLoader,
            context_service: NotificationContextServiceBase
    ):
        template = template_loader.get_template(template_name)
        super().__init__(template_loader, TemplateNotificationFactory(
            template,
            TemplateActionsBuilder(template)
        ))
        self._context_service = context_service

    def create_notification(self, user: AbstractUser, invitation: ProjectInvitation, **kwargs) -> Notification:
        notification = super().create_notification(user, invitation)

        self._context_service.create_context(
            notification,
            {'project': invitation.project}
        )
        return notification


class ProjectInvitationService:
    def __init__(self, notification_service: NotificationServiceBase[ProjectInvitation]):
        self._notification_service = notification_service

    def accept_invitation(self, user: AbstractUser, invitation: ProjectInvitation) -> None:
        self._handle_expired_invitation(user, invitation)
        self._notification_service.update_notification_by_action(user, invitation, 'accept')
        invitation.accept()

    def reject_invitation(self, user: AbstractUser, invitation: ProjectInvitation) -> None:
        self._handle_expired_invitation(user, invitation)
        self._notification_service.update_notification_by_action(user, invitation, 'reject')
        invitation.reject()

    def _handle_expired_invitation(self, user, invitation: ProjectInvitation):
        if not invitation.is_expired():
            return
        notification = self._notification_service.get_notification(user, invitation)
        update_notification_footer(
            notification,
            footnote=settings.INVITATION_IS_EXPIRED_MESSAGE,
            clear_actions=True
        )
        raise ProjectInvitationIsExpiredError(settings.INVITATION_IS_EXPIRED_MESSAGE)

    def delete_invitation(self, user: AbstractUser, invitation: ProjectInvitation) -> None:
        invitation.delete()
        self._notification_service.delete_notification(user, invitation)

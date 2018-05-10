from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field, user_username

# Perform custom tweaks when setting up a user from Office 365
class OverrideSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # Use userPrincipalName as email and get their network ID from it for
        # a username
        user_principal_name = sociallogin.account.extra_data['userPrincipalName']
        email = user_principal_name.lower()
        username = email.split('@', 1)[0]

        # These other ones are already set for us in data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        user = sociallogin.user
        user_username(user, username)
        user_email(user, email)
        user_field(user, 'first_name', first_name)
        user_field(user, 'last_name', last_name)
        return user

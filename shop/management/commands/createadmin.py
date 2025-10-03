from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Create an admin user for JEETECH admin panel'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')
        parser.add_argument('--make-existing-admin', type=str, help='Make existing user admin by username')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== JEETECH Admin User Creator ===\n'))

        # Check if making existing user admin
        if options['make_existing_admin']:
            return self.make_existing_admin(options['make_existing_admin'])

        # Get user input if not provided via arguments
        username = options['username'] or input('Enter admin username: ')
        email = options['email'] or input('Enter admin email: ')
        password = options['password'] or input('Enter admin password: ')

        if not username or not password:
            self.stdout.write(self.style.ERROR('Username and password are required!'))
            return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists!'))
            existing_user = User.objects.get(username=username)
            if existing_user.is_staff:
                self.stdout.write(self.style.WARNING(f'User "{username}" is already an admin user.'))
            else:
                make_admin = input(f'Make existing user "{username}" an admin? (y/n): ').lower()
                if make_admin == 'y':
                    return self.make_existing_admin(username)
            return

        try:
            # Create the admin user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(self.style.SUCCESS(f'\n✅ Admin user "{username}" created successfully!'))
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Staff: {user.is_staff}')
            self.stdout.write(f'   Superuser: {user.is_superuser}')
            self.stdout.write('\n🎉 You can now login to the admin panel with these credentials!')
            self.stdout.write('   Admin Panel: http://localhost:8000/admin/')
            self.stdout.write('   JEETECH Admin: Navigate to "Admin" in the main site after login')

        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Validation error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {e}'))

    def make_existing_admin(self, username):
        """Make an existing user an admin"""
        try:
            user = User.objects.get(username=username)
            
            if user.is_staff and user.is_superuser:
                self.stdout.write(self.style.WARNING(f'User "{username}" is already a superuser admin.'))
                return
            
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ User "{username}" is now an admin!'))
            self.stdout.write(f'   Email: {user.email}')
            self.stdout.write(f'   Staff: {user.is_staff}')
            self.stdout.write(f'   Superuser: {user.is_superuser}')
            self.stdout.write('\n🎉 They can now access the admin panel!')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist!'))
            
            # Show available users
            users = User.objects.all()
            if users.exists():
                self.stdout.write('\nAvailable users:')
                for user in users:
                    status = []
                    if user.is_staff:
                        status.append('Staff')
                    if user.is_superuser:
                        status.append('Superuser')
                    status_str = f" ({', '.join(status)})" if status else ""
                    self.stdout.write(f'  - {user.username} ({user.email}){status_str}')
            else:
                self.stdout.write('No users found in the system.')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating user: {e}'))

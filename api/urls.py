from django.conf.urls import url
from .views import user, admin_user, project, home

# namespacing app
app_name = 'api'

urlpatterns = [

    # User-auth routes
    url('user/login/', user.LoginFormView.as_view(), name='user-login'),
    url('user/logout/', user.LogoutView.as_view(), name='user-logout'),
    url('user/register/', user.RegisterFormView.as_view(), name='user-register'),
    url('user/verify_email/', user.VerifyEmail.as_view(), name='verify-email'),
    url('user/pass_reset/', user.ResetPassRequest.as_view(), name='user-pass-reset'),
    url('user/pass_update/', user.ResetPassUpdate.as_view(), name='user-pass-update'),

    # Admin-user routes
    url('admin_users', admin_user.AllUsers.as_view(), name='admin-users'),
    url('admin_user/project/', admin_user.Profile.as_view(), name='project-profile'),
    url('admin_user/update_roles/', admin_user.AssignRoles.as_view(), name='update-roles'),
    url('admin_user/create_tags/', admin_user.CreateTags.as_view(), name='create-tags'),
    url('admin_user/add_members/', admin_user.AddMembers.as_view(), name='add-members'),

    # Project routes
    #search route: pass a parameter type (name, prof, interest, tag) and value
    url('projects', project.AllProjects.as_view(), name='projects-all'),
    url('project/search', project.Search.as_view(), name='search'),
    # create route 
    url('project/create', project.Create.as_view(), name='project-create'),
    # edit route 
    url('project/edit', project.Edit.as_view(), name='project-edit'),
    # write route
    url('project/write', project.Write.as_view(), name='project-write'),
    #Tags
    url('project/tags', project.Tags.as_view(), name='tags'),
    
    #AOR
    url('aor', home.AllAor.as_view(), name='aor-all'),
    #Departments
    url('department', home.AllDepartments.as_view(), name='departments-all'),
    #Centers
    url('center', home.AllCenters.as_view(), name='centers-all'),
]

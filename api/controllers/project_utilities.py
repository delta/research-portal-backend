from api.models import Project, ProjectMemberPrivilege, ProjectMemberRelationship
import logging

logger = logging.getLogger(__name__)

def create_project(name, abstract, paper_link, head, department, aor):
    """
        Helper to create project and assign project user relationship
    """
    try:
        # project_member_privilege = ProjectMemberPrivilege.objects.filter(name = "Admin")
        if head.is_staff:
            project = Project.objects.create(name = name, abstract = abstract, paper_link = paper_link, head = head, department = department, aor = aor)
            ProjectMemberRelationship.objects.create(project = project, user = head, privilege = project_member_privilege[0])
            return True
        else:
            logger.error("Admin access not found")
            return False
    except Exception as e:
        logger.error(e)
        return False

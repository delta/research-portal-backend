from api.models import COE, AreaOfResearch, Labs, Project, ProjectMemberPrivilege, ProjectMemberRelationship
import logging

logger = logging.getLogger(__name__)

def create_project(name, abstract, paper_link, head, department, tags, aor, labs, coes):
    """
        Helper to create project and assign project user relationship
    """
    try:
        project_member_privilege = ProjectMemberPrivilege.objects.filter(name = "Admin")
        if head.is_staff:
            project = Project.objects.create(name = name, abstract = abstract, paper_link = paper_link, head = head, department = department, tags = tags)
            aor_set = AreaOfResearch.objects.filter(name__in=aor)
            labs_set = Labs.objects.filter(name__in=labs)
            coes_set = COE.objects.filter(name__in=coes)
            project.aor_tags.add(*aor_set)
            project.labs_tags.add(*labs_set)
            project.coe_tags.add(*coes_set)
            ProjectMemberRelationship.objects.create(project = project, user = head, privilege = project_member_privilege[0])
            return True
        else:
            logger.error("Admin access not found")
            return False
    except Exception as e:
        logger.error(e)
        return False

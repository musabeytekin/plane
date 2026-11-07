# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from django.urls import resolve, reverse
from rest_framework import status

from plane.api.views.estimate import ProjectEstimateAPIEndpoint
from plane.db.models import Project, ProjectMember


@pytest.fixture
def project(db, workspace, create_user):
    project = Project.objects.create(
        name="Estimate Project",
        identifier="EP",
        workspace=workspace,
        created_by=create_user,
    )
    ProjectMember.objects.create(project=project, member=create_user, role=20, is_active=True)
    return project


@pytest.mark.contract
class TestEstimateRouting:
    def test_estimate_url_resolves_to_view(self, workspace, project):
        url = f"/api/v1/workspaces/{workspace.slug}/projects/{project.id}/estimates/"
        assert resolve(url).func.view_class is ProjectEstimateAPIEndpoint
        assert reverse("project-estimate", kwargs={"slug": workspace.slug, "project_id": project.id}) == url

    @pytest.mark.django_db
    def test_estimate_endpoint_reaches_view(self, api_key_client, workspace, project):
        url = f"/api/v1/workspaces/{workspace.slug}/projects/{project.id}/estimates/"
        response = api_key_client.get(url)
        # Reaching the view means we do not get Django's "Page not found." 404.
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"error": "Estimate not found"}

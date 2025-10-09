Feature: Create repository-workflow map
  As a developer
  I want to map repositories to their corresponding workflows
  So that I can easily identify which workflows belong to which project

  Scenario: Successfully create a repository to workflow mapping
    Given the following workflow filenames are available:
      | filename           |
      | frontend_build.json |
      | frontend_deploy.json |
      | backend_test.json  |
      | backend_build.json |
    When I call create_repo_workflow_map
    Then I should get a dictionary mapping repositories to workflows
    And each repository should have a list of workflow names

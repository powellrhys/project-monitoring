Feature: Collect project workflows
  As a developer
  I want to retrieve a list of workflow files from the project-monitoring container
  So that I can monitor the workflows available in my projects

  Scenario: Successfully collect workflow filenames
    Given the following workflow filenames are available in container:
      | filename                   |
      | workflows/build_pipeline.json |
      | workflows/deploy_pipeline.json |
      | workflows/test_pipeline.json   |
    When I call collect_project_workflows
    Then I should get a list of workflow filenames
    And each filename should be a string ending with ".json"
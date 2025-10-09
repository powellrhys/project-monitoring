Feature: Collect latest workflow runs
  As a developer
  I want to gather the most recent workflow run from each workflow file
  So that I can analyze the latest status of all projects

  Scenario: Successfully collect the most recent workflow runs
    Given the following workflow data files are available:
      | filename                      | id | status  | workflow       |
      | workflows/frontend_build.json | 1  | success | frontend_build |
      | workflows/backend_test.json   | 2  | failed  | backend_test   |
    When I call collect_latest_workflow_runs
    Then I should get a pandas DataFrame
    And each row should represent the most recent run for each workflow

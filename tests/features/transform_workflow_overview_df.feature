Feature: Transform workflow overview DataFrame
  As a developer
  I want to transform workflow data for presentation
  So that I can display it in the dashboard

  Scenario: Successfully transform workflow data
    Given the following workflow data:
      | repo      | workflow_name | updated_at              | status  | html_url                                              | duration_seconds |
      | frontend  | build         | 2025-09-29T12:00:00Z    | success | https://github.com/powellrhys/frontend/actions/1      | 125              |
      | backend   | test          | 2025-07-29T12:00:00Z    | failed  | https://github.com/powellrhys/backend/actions/2       | 310              |
    When I call transform_workflow_overview_df
    Then I should get a transformed pandas DataFrame
    And it should contain formatted durations, URLs, and status flags

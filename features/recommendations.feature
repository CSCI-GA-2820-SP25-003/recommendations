Feature: Recommendation Service

  Background:
    Given the following recommendations
        | id | product_id | customer_id | product_name | recommendation_name | recommend_product_id | recommend_type | rec_success |
        | 1  | 1          | 101         | cake         | cookie              | 123                  | Cross-Sell     | 1           |
        | 2  | 2          | 102         | lemon        | orange              | 321                  | Cross-Sell     | 0           |
        | 3  | 3          | 103         | pineapple    | mango               | 456                  | Cross-Sell     | 1           |
        | 4  | 4          | 104         | water        | sparkling water     | 654                  | Up-Sell        | 1           |
        | 5  | 5          | 105         | sprite       | coke                | 111                  | Cross-Sell     | 0           |

  Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation Demo RESTful Service" in the title
    And I should not see "404 Not Found"

  Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I switch to the "Create" tab
    And I set the "product_id" to "6"
    And I set the "customer_id" to "201"
    And I set the "product_name" to "chips"
    And I set the "recommendation_name" to "dip"
    And I set the "recommend_product_id" to "888"
    And I select "Cross-Sell" in the "recommend_type" dropdown
    And I set the "rec_success" to "1"
    And I press the "Create" button
    Then I should see the message "Success"

  Scenario: List all Recommendations
    When I visit the "Home Page"
    And I switch to the "Read" tab
    And I press the "List Read" button
    Then I should see "cake" in the results
    And I should see "lemon" in the results
    And I should see "sprite" in the results

  Scenario: Retrieve by ID
    When I visit the "Home Page"
    And I switch to the "Read" tab
    And I set the "read_id" to "27"
    And I press the "Retrieve" button
    Then I should see "cake" in the results

  Scenario: Filter by Recommendation Type
    When I visit the "Home Page"
    And I switch to the "Read" tab
    And I select "Cross-Sell" in the "recommend_type" dropdown
    And I press the "Filter Search" button
    Then I should see "lemon" in the results
    And I should not see "water" in the results

  Scenario: Filter by Product Name
    When I visit the "Home Page"
    And I switch to the "Read" tab
    And I set the "read_product_name" to "cake"
    And I press the "Filter Search" button
    Then I should see "cake" in the results
    And I should not see "lemon" in the results

  Scenario: Filter by Success Rate Range
    When I visit the "Home Page"
    And I switch to the "Read" tab
    And I set the "rec_success_min" to "1"
    And I set the "rec_success_max" to "1"
    And I press the "Filter Search" button
    Then I should see "cake" in the results
    And I should not see "lemon" in the results

  Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I switch to the "Update" tab
    And I set the "update_id" to "47"
    And I set the "update_product_name" to "treat"
    And I press the "Update" button
    Then I should see the message "Update success!"

  Scenario: Like a Recommendation
    Given the following recommendations
        | id | product_id | customer_id | product_name | recommendation_name | recommend_product_id | recommend_type | rec_success |
        | 1  | 1          | 101         | cake         | cookie              | 123                  | Cross-Sell     | 1           |
    When I visit the "Home Page"
    And I switch to the "Update" tab
    And I set the "update_id" to "57"
    And I press the "Like" button
    Then I should see the message "Liked! Success rate increased."

  Scenario: Delete a Recommendation
    When I visit the "Home Page"
    And I switch to the "Delete" tab
    And I set the "delete_id" to "59"
    And I press the "Delete ID" button
    Then I should see the message "Recommendation deleted successfully."
    
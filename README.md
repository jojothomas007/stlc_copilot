Poetry:

Dependency management and packaging:
poetry is a tool for dependency management and packaging in Python.
It uses pyproject.toml for configuration.

Install: pip install poetry
Create: poetry new myproject
Initialize in existing project: poetry init
Activate: poetry env activate
Install packages: poetry add package_name

<!-- For Bringing up the server -->
poetry run uvicorn src.stlc_copilot.main:app --reload


https://github.com/Python-World/python-mini-projects/tree/master



BDD Testcase Generation Pompt
*****************************
Please generate bdd testcases from below userstory description. Generated Output must be in the json format : { "feature": "Feature name in less than 50 characters", "scenarios": [ { "name": "Scenario name in less than 50 characters", "description": "Scenario description in less than 200 characters", "steps": "All Scenario steps formatted and each in new line" }]} Userstory summary : As a customer, I want to be able to easily track my insurance claim in real-time using a user-friendly mobile app or online portal. Userstory Description:The claims tracking feature should provide me with up-to-date information on the status and progress of my claim. It should also allow me to access related documents and communicate directly with my insurer.

BDD Testcase Generated
**********************
{
    "feature": "Claims Tracking",
    "scenarios": [
        {
            "name": "View claim status in real-time",
            "description": "Customer views the status of their insurance claim in real-time.",
            "steps": "Given I am logged into the mobile app or online portal\nWhen I navigate to the claims tracking section\nThen I should see the current status of my submitted claim\nAnd the status should be updated in real-time according to the latest information"
        },
        {
            "name": "Access related documents",
            "description": "Customer accesses related documents of their insurance claim.",
            "steps": "Given I am logged into the mobile app or online portal\nWhen I navigate to the claims tracking section\nAnd I click on the claim in question\nThen I should be able to access all related documents (e.g., receipts, correspondence)\nAnd the documents should be displayed correctly"
        },
        {
            "name": "Communicate with the insurer",
            "description": "Customer communicates directly with the insurer regarding their claim.",
            "steps": "Given I am logged into the mobile app or online portal\nWhen I navigate to the claims tracking section\nAnd I click on the claim in question\nThen I should be able to communicate directly with my insurer\nAnd I should be able to send and receive messages regarding my claim"
        }
    ]
}

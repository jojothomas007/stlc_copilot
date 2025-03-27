**STLC Assistant**

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

JIRA API
********
https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-links/#api-rest-api-3-issuelink-post

Confluence API
**************
https://docs.atlassian.com/ConfluenceServer/rest/7.19.16/#api/content-getContent

Zephyr Scale
************
https://support.smartbear.com/zephyr-scale-cloud/docs/en/rest-api/api-access-tokens-management.html
https://support.smartbear.com/zephyr-scale-cloud/api-docs

XRAY API
********
https://docs.getxray.app/display/XRAYCLOUD/Importing+Tests+-+REST+v2
https://docs.getxray.app/display/XRAYCLOUD/Exporting+Cucumber+Tests+-+REST+v2

Get XRAY API credentials
https://docs.getxray.app/display/XRAYCLOUD/Global+Settings%3A+API+Keys


GITHUB API
**********
https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28&tool=curl

Get Branch
https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#get-a-branch
curl -L -H "User-Agent: stlc_copilot" -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ghp_token" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/jojothomas007/cucumber-java/branches/test1

create branch
https://docs.github.com/en/rest/git/refs?apiVersion=2022-11-28#create-a-reference
curl -L -X POST -H "User-Agent: stlc_copilot" -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ghp_token" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/jojothomas007/cucumber-java/git/refs -d "{\"ref\":\"refs/heads/featureA\",\"sha\":\"ef32440eecc86b82400d8ba0bc6601ead904888c\"}"

create-or-update-file-contents
https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#create-or-update-file-contents
curl -L -X PUT -H "User-Agent: stlc_copilot" -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ghp_token" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/jojothomas007/cucumber-java/contents/src/new_file.txt -d "{\"message\":\"Commit message\",\"committer\":{\"name\":\"Jojo Thomas\",\"email\":\"jojothomas007@gmail.com\"},\"content\":\"bXkgbmV3IGZpbGUgY29udGVudHM=\",\"branch\":\"test1\"}"

create pull request
https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#create-a-pull-request
curl -L -X POST -H "User-Agent: stlc_copilot" -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ghp_token" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/jojothomas007/cucumber-java/pulls -d "{\"title\":\"Amazing new feature\",\"body\":\"Please pull these awesome changes in!\",\"head\":\"test1\",\"base\":\"main\"}"


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

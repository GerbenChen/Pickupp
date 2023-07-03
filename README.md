# Pickup Automation Test Framework

### Directory Structure
```
├── Readme.md              // help.
├───.circleci
│       config.yml         // The circleci configuration file.
├───BulkOrderFile          // BulkOrder test case for selenium.
├───Config                 // Feature configuration and pre-condition file.
├───Core                   // Core API method folder.
├───Library                // Public library folder.
├───Method                 // Logic or data processing method folder.
├───NoUse                  // The file not use in automation scope.
├───OrderCreation          // Main API automation scenario folder, include Admin/Merchant/DA test.
├───SOP                    // Purchase Order test scenario folder.
├───Tools                  // Common tools folder.
│       requirements.txt   // Stores the libraries, modules, and packages that are used while developing a project.
├───Utility                // Interfaces for third-party applications folder.
└───V3                     // V3 test scenario temp folder.
```

## Run in Circleci
When you are ready for automated test case, please remember to add the test case script to config.yml.

Please refer to the following example for the format:
```
- run:
    name: OrderFlow
    command: |
      python ./OrderCreation/SingleOrderFlow.py
```

## Test Case Recommend

### Fill Test Step Result
If you want to fill status in your test step, please refer to the following:
```
The ID of the test status. The default system statuses have the following IDs:
1: Passed
   resultList.extend((FrameworkVar.ApiSpentTime, True, result_massage))
2: Blocked
   resultList.extend((FrameworkVar.ApiSpentTime, "Blocked", result_massage))
3: Untested (not allowed when adding a new result)
   resultList.extend((FrameworkVar.ApiSpentTime, "Untested", result_massage))
4: Retest
   resultList.extend((FrameworkVar.ApiSpentTime, "Retest", result_massage))
5: Failed
   resultList.extend((FrameworkVar.ApiSpentTime, False, result_massage))
```

### Mapping with TestRail

1. Please add your test case in testrail.ini, For format requirements, please refer to the following:
```
[Job Flow]
suite_id =319
case_ids =5680,5681,9538,9586,9588
```
2. Please add the following section to the end of your test case, For format requirements, please refer to the following:
```
# Final : Update result to testrail
CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5680", resultList, self.test_case_time_start)
```

## Test report
We use testrail to create automated test reports, please visit testrail or ask a team member.

## Notice
If you use additional libraries, modules and packages, please remember to store them in requirements.txt
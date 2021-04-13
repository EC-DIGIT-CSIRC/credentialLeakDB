# Pull request template

The model we are using is to have a fork of the repo, edit on the fork, then 
make a pull request. The PR needs then to be reviewed and 
merged into the ``main``  branch.
It will be sent through a couple of quality checks and if it does
not meet those, the PR needs to be adapted.

# Description
New tool, Bug fixing, or Improvement?  
Please include a summary of the change and which issue is fixed. Also include relevant motivation and context.

## Related issue

## Check list
- [ ] Related issue / work item is attached
- [ ] Unit-tests are written (if applicable)
- [ ] Documentation is updated (if applicable)
- [ ] Changes are tested, tests pass, no code linting errors and no high/critical vulnerabilities identified in codebase.

## Testing
- [ ] Did you write new unit tests for this change?
- [ ] Did you write new integration tests for this change?
  Include the test commands you ran locally to test this change
  e.g.:
```bash
pytest -v <mydirectory>
```

## Monitoring
- [ ] Will this change be covered by our existing monitoring? (no new canaries/metrics/dashboards/alarms are required)
- [ ] Will this change have no (or positive) effect on resources and/or limits?
  (including CPU, memory, AWS resources, calls to other services)
- [ ] Can this change be deployed to Prod without triggering any alarms?

## Rollout
- [ ] Can this change be merged immediately into the pipeline upon approval?
- [ ] Are all dependent changes already deployed to Prod?
- [ ] Can this change be rolled back without any issues after deployment to Prod?




This is the template we use in our projects.

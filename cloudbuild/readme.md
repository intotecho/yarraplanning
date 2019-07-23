# Cloud Build configuration to Build Critical Views for Heritage Maps

Cloud Build has access to this git repo.
It can trigger a build, but for now this is manually triggered.

[Cloud Build Console](https://console.cloud.google.com/cloud-build)

It is part of a CI/CD data pipeline.

#Dependencies

The build  does not load the tables created by  python scripts, but depends on them. These tables are stored in the Dataset yarraPlanning.


## Environments

Prod and Dev should have different DataSets. TBD.

## Substitutions

There are substitution parameters in the script.
- _TARGET_DATASET: YarraPlanning
- _SOURCE_DATASET: YarraPlanning
- _PROJECT_ID: yarrascrape
- _HERITAGE_PROPS_VIEW: HERITAGE_OVERLAY_WITH_ADDR_AND_PROPERTY
- _OVERLAYS_AVG_DATE: OVERLAYS_AVG_ESTABLISHED_DATE
- _OVERLAYS_VIEW: OVERLAYS
- _YARRAHERITAGEMAPS_PROPERTIES: YARRAHERITAGEMAPS_PROPERTIES

These can be overridden in the cloud build console.






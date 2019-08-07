# Heritage Explorer User Guide

## What is Heritage Explorer

Heritage Explorer presents published heritage information in an
accessible spatial format.

By incorporating heritage data from multiple sources, it generates a cohesive
 view of the heritage in a precinct.

Clicking on an Overlay will load and display the heritage places within that overlay. Each place is shaded in a colour determined by its heritage grading.

Clicking on a site will show detailed heritage information for that site in the Heritage Site Details Panel at the bottom of the screen. You can drag this screen up or down using the dragger above the title:

- Make it bigger to see larger photos.
- Make it smaller to see more of the map.

Clicking the **>** icon on the top left of the title bar opens a menu. This allows:

- Change the shading option from grading to age of site.
- Select another overlay by HO number.
- Display selected historic maps prepared by the MMBW in the early 1900s.
- Display Planning Applications for the selected overlay.

## Who is it for?

The intended use is for  research and education.

The Heritage Explorer is not a definitive reference source and should not be
 used for statutory purposes such as preparing or reviewing a development application.

## How correct is the data?

The data is provided without guarantees of accuracy or maintenance.

While all the data is derived from official sources, a lot of data
 processing is needed to generate the final result. This can lead to errors.

The official data has many gaps and inconsistencies. It can be difficult to
 determine the title boundaries directly from the official data. See [Mapping Spatial Data](#-Mapping-Spatial-Data).

Heritage data does not change rapidly.  Changes do occur as the result of
 planning scheme amendments, demolitions, new development and new research. The State Government and the Council are forever adjusting planning controls to suit different agendas.

## Official Data Sources and Currency

- Heritage Overlay boundaries - Victorian Spatial Data Mart, April 2019.
- Overlay Controls from Yarra Planning Scheme Clause 43.01 Heritage Schedules -
 current in May 2019.
- Site specific data from Database of Heritage Significant Areas - January 2019 (C191)
- Victorian Heritage Database - May 2019. Photos are current. They are loaded
 on demand from the VHD.
- The planning applications go up to 31 December 2018.
- MMBW overlays are from 1900-1904 based on surveys from earlier years.

## Heritage Data

The main value of the Heritage Explorer is that it presents
 complex heritage data in a spatial format.

There are no published maps of Heritage Places in the City of
 Yarra. Occasionally, a map may be prepared for a heritage study
 of a precinct. Such maps are only published in reports.

The title number is not recorded in the Yarra Database of Heritage Significant Places.
 The find the title boundary, it is necessary to match the address or yarra
  property number to a title.  See [Mapping Spatial Data](#-Mapping-Spatial-Data).

The Yarra Database of Heritage Significant Places was originally prepared by
Graeme Butler & Associates for the [City of Yarra Review of Heritage Overlay
Areas](https://www.yarracity.vic.gov.au/the-area/heritage/heritage-studies)
in 2007 and formed Appendix 8 of that report.

This document provides gradings for individual sites, and an overall statement of
significance for the precinct Heritage Overlays. It also lists sites that are
 registered on the Victorian Heritage Register. These are among the most
 significant sites in the state. Heritage Victoria is the responsible
  authority for managing the heritage conservation of these sites.
  Each sites on the VHR has its own VHR overlay, as well as potentially
  being inside one of Yarra's Overlays.

VHR Overlays are shown with a red outline on the map. This denotes their higher level of significance and different responsible authority.

Overlays in the Yarra Planning Scheme are denoted with a black outline on the map.

### Heritage Planning Controls

[Clause 43.01 HERITAGE OVERLAY](http://planningschemes.dpcd.vic.gov.au/schemes/vpps/43_01.pdf) of the Yarra Planning Scheme is the main planning control for heritage overlays. This states that a permit is required to

- Subdivide land.
- Demolish or remove a building.
- Construct a building or construct or carry out works
  before a building in a heritage overlay may be demolished
or constructed.

Many controls apply to all overlays in the city, but some are overlay specific.

Individual Overlay Controls are contained in the [Schedule to the Heritage Overlay](http://planningschemes.dpcd.vic.gov.au/schemes/vpps/43_01s.pdf).

For each overlay in the City of Yarra, this table states what
controls apply. These may include any of the following.

| Control         | Meaning      |
| ------------- |:------------|
| Tree Controls      | "Tree Controls apply in this overlay. A Permit is required to remove, destroy or lop a tree This does not apply To any action which is necessary to keep the whole or any part of a tree clear of an electric line provided the action is carried out in accordance with a code of practice prepared under Section 86 of the Electricity Safety Act 1998. If the tree presents an immediate risk of personal injury or damage to property.
| Paint Controls| A Permit is required to Externally paint a building.|
| Internal Controls | A Permit is required to Internally alter a building.
| Fence Controls      | A permit is not required for Demolition or removal of an outbuilding (including a carport, garage, pergola, verandah, deck, shed or similar structure unless the outbuilding is specified in the schedule to this overlay. |
| Prohibited uses may be permitted | A permit may be granted to use a heritage place for a use which would otherwise be prohibited if all of the following apply: The schedule to this overlay specifies the heritage place as one where prohibited uses may be permitted.      The use will not adversely affect the significance of the heritage place.       The benefits obtained from the use can be demonstrably applied towards the conservation of the heritage place. |
| Aboriginal Heritage Place| A heritage place specified in the schedule to this overlay as an Aboriginal heritage place is also subject to the requirements of the Aboriginal Heritage Act 2006. |
|

The Heritage Explorer shows the name on in the left column in the site details panel.
This is a shorthand to quickly see what controls apply.

If Tree Controls apply to the overlay, the Heritage Explorer shades the overlay green on the map.

Clause 43.01-6 allows Heritage Design Guidelines for any heritage place included in
the schedule. For Yarra, these are contained in Clause 22.02 of the Planning Scheme:
 [Development Guidelines for Heritage Places](http://planningschemes.dpcd.vic.gov.au/schemes/yarra/ordinance/22_lpp02_yara.pdf).

The schedule also provides: 

- A name for the heritage site
- Identifies whether the site has an incorporated plan and
- Whether the site is Interim and has an expiry date.
- The corresponding VHR number, if any.

This information is displayed in the overlay panel or site details panel.

If the Overlay is Interim, the Heritage Explorer shades the overlay yellow on the map to make them easier to find and identify.

The Heritage Schedule is a difficult to read PDF table. The format was defined by Heritage Victoria a decade ago and used by all councils. To make it useful, the data for almost 500 overlays was converted to a table using complex data transformations, and some manual updates.

## Mapping Spatial Data

### Overlays

Mapping the heritage overlay boundaries is straightforward.
The boundaries of all overlays, not just heritage overlays, are publicly available in GIS format from the Victorian Government Spatial Data Mart. So it is only necessary to filter the overlays to Heritage in Yarra. Data for each overlay is joined with the  Heritage Schedule.

For Overlays with a VHR Number (shown in red on the map), the Heritage Explorer also displays a photo in the overlay panel. It uses the VHR number to search the Victorian Heritage Database and fetches the photo for the VHD.

### Heritage Sites

Mapping individual heritage sites is more difficult. To find a location, the site's title boundary must be determined. There are several ways to do this, but none of the ways will work in all cases. Some of the techniques are:

#### Property Number

The Yarra property number is not widely used outside Yarra's own systems
 and processes. In the heritage database, the property number may be
 incorrect, or non existent. It was not relied upon as a data reference.
If the property number is correct, then the title can be determined from the VicMap Property GIS file. This is a cadaster of title boundaries.

##### Issues

- Subdivisions and Consolidations can change the property number.
- Sites may be recorded with the wrong number that refers to another site. 
- Sites may be recorded with a duplicate of another site.
- The property might not exist.
- Some sites do not have a property number, for example, bridges or parks.

#### Address Matching

The address of the heritage place can be compared to the official list of postal addresses.
This data is publicly available. Once an official address is found, the property indicator (PFI, not the council property number) can be used to look up the title boundary in the cadaster.

##### Issues

- Many sites in the heritage register have a non standard address
- Address may be written in a non-standard format.
- Address may include other details like (rear of, below, in front of)
- Site might not be addressable, such as parks, bridges and even some churches.
- There may be multiple sites that match the same address.
- Addresses can be in a range in the register, and individual in the standard.
- Addresses can be single in the register, and in a range in the standard.
- Address in the register that once referred to a factory now match multiple apartments.
- Addresses in the register is wrong, eg. Burnley or Cremorne instead of Richmond
- Spelling

Strategies for each of this issues have been used to match an address promiscuously. This can lead to multiple overlapping sites showing on the map.

#### VHD Matching

Nearly all the heritage sites in the Yarra Heritage Database are also recorded in the Victorian Heritage Database (VHD). The VHD records a location (latitude and longitude) for each place (source unknown) and uses this to draw a pin on a map.
Unfortunately, there is no reliable key for matching places in the register to the VHD, so again address has to be used. The two databases display address differently.

Matching to the VHD provides access to other sources of information about the place, such as photographs, a Statement of Significance and references to heritage studies.

The VHD location is useful when no title can be reliably found. Also, when other matching strategies find multiple titles, the VHD location can be used as a check to see which is most likely correct.

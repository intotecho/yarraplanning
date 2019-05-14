export class SelectMMBWOverlay {
    MMBWmapId: String;
    KMLurl: String;
    citation: String;
    onlineLink: String;
    catalogueLink: String;
    date: Date;
}


export const MMBWMapsLibrary: Array<SelectMMBWOverlay> =[
    {
        MMBWmapId: 'MMBW1264 Fitzroy & Collingwood (1904)',
        KMLurl: '../../../assets/MMBW/MMBW_1264.kml',
        citation: `MAP
        Melbourne and Metropolitan Board of Works detail plan, 1264, Fitzroy & Collingwood.
        Melbourne and Metropolitan Board of Works`,
        onlineLink: 'http://handle.slv.vic.gov.au/10381/117717',
        catalogueLink: 'http://search.slv.vic.gov.au/MAIN:Everything:SLV_VOYAGER1164426',
        date: new Date('1904/01/01')
    },
    {
        MMBWmapId: 'MMBW Detail Plan 1239',
        KMLurl: '../../../assets/MMBW/MMBW_1239.kml',
        citation: `MAP
        Melbourne and Metropolitan Board of Works detail plan, 1239, Fitzroy.
        Melbourne and Metropolitan Board of Works`,
        onlineLink: 'http://handle.slv.vic.gov.au/10381/117716',
        catalogueLink: 'http://search.slv.vic.gov.au/MAIN:Everything:SLV_VOYAGER1164906',
        date: new Date('1900/01/01')
    }
    ];




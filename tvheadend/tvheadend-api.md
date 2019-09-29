# TVHeadend API Notes
Routes are all of the form

```
http://127.0.0.1:9981/api/<route>
```

## Finished Recordings
route: `dvr/entry/grid_finished`
returns: dict

```
recordings: {
    'entries': [
        {
            'uuid': 'c0ee5c440e57b22b451d537ef3536a0f',
            'enabled': True,
            'start': 1555086600,
            'start_extra': 0,
            'start_real': 1555086570,
            'stop': 1555088400,
            'stop_extra': 0,
            'stop_real': 1555088400,
            'duration': 1800,
            'channel': '0444a0855ff0f4abfe561776c1258270',
            'channel_icon': 'https://s3.amazonaws.com/schedulesdirect/assets/stationLogos/s99024_h3_aa.png',
            'channelname': 'Talking Pictures TV',
            'title': {'eng': "Robin's Nest"},
            'disp_title': "Robin's Nest",
            'subtitle': {'eng': 'Dinner Date'},
            'disp_subtitle': 'Dinner Date',
            'description': {'eng': "Nicholls' former girlfriend, Davinia, reappears."},
            'disp_description': "Nicholls' former girlfriend, Davinia, reappears.",
            'pri': 2,
            'retention': 0,
            'removal': 0,
            'playposition': 0,
            'playcount': 0,
            'config_name': 'ee86fd19903e87679e5fdfe243966ad0',
            'owner': 'chris',
            'creator': 'chris',
            'filename': "/home/hts/Robin's-Nest-S03E07.ts",
            'errorcode': 0,
            'errors': 0,
            'data_errors': 0,
            'dvb_eid': 0,
            'noresched': True,
            'norerecord': False,
            'fileremoved': 0,
            'autorec': '45d44ebd0ae899e0fd84448f87c45685',
            'autorec_caption': ' (Created from EPG query)',
            'timerec': '',
            'timerec_caption': '',
            'parent': '',
            'child': '',
            'content_type': 0,
            'broadcast': 0,
            'episode': 'Season 3.Episode 7',
            'url': 'dvrfile/c0ee5c440e57b22b451d537ef3536a0f',
            'filesize': 324759552,
            'status': 'Completed OK',
            'sched_status': 'completed',
            'duplicate': 0,
            'comment': 'Auto recording: Created from EPG query'
        },
        {
        ...
        }
    ],
    'total': 18
}
```

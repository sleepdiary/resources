#!/usr/bin/env node

/*
 * Load resources, and derive some widely-used properties
 */

const http  = require('http');
const https = require('https');
const url   = require('url');
const yaml = require('js-yaml');
const fs   = require('fs');
const child_process = require('child_process');

const output = {};

const valid_specialist_types = {
    physician: "a medical doctor who treats sleep disorders",
    researcher: "an academic who studies sleep disorders",
};

const valid_referral_types = {
    direct: 'a specialist who takes referrals directly from individuals',
    'secondary': 'a specialist who only takes referrals from general practitioners (UK) or primary care physicians (US)',
    tertiary: 'a specialist who only takes referrals from other specialists',
};

const valid_procedure_types = {
    researched: 'the "procedure" data has been researched by us (e.g. by reading the website)',
    confirmed: 'the "procedure" data has been confirmed by someone with direct experience (e.g. a doctor or patient)',
};

function zero_pad(n,len) {
    n = n.toString();
    while ( n.length < (len||2) ) n = '0'+n;
    return n;
}

const multipliers = {
    day: 1,
    week: 7,
    month: 30,
};
function to_duration(d) {
    let ret=0;
    d.replace(
        /^([0-9]+) (day|week|month)s?$/i,
        (_,base,multiplier) => ret = parseInt(base,10) * multipliers[multiplier.toLowerCase()]
    );
    if ( !ret ) {
        throw Error(`Could not convert ${d} to duration`);
    }
    return zero_pad(ret,4);
}

function to_time(t) {
    switch ( t.toLowerCase() ) {
    case 'midnight': return "00";
    case 'noon'    : return "12";
    default:
        let ret;
        t.replace(
            /^([0-9]+) *([ap])m$/i,
            (_,n,ap) => ret = parseInt(n,10) + (ap=='a'?0:12)
        );
        if ( !ret ) {
            throw Error(`Could not convert ${t} to time`);
        }
        return zero_pad(ret,2);
    }
}

const name_preamble = /^(?:mr|mrs|miss|ms|dr|the)\b/i;

[ 'specialists', 'software' ].forEach( source => {

    const records = (

        // Load:
        yaml.load(
            fs.readFileSync(
                __filename.replace(/[^\/]*$/,`entities/${source}.yaml`),
                'utf8'
            )
        )

        // Process:
        .map( p => {

            p.name_key = p.name.replace(name_preamble,'').toLowerCase().replace(/^[. ]*/,'');

            // Convert "foo bar-baz" to "foo_barbaz":
            const convert_keys = obj => {
                if ( Array.isArray(obj) ) {
                    obj.forEach( convert_keys );
                } else if ( typeof(obj) == "object" ) {
                    Object.keys(obj).forEach( key => {
                      const value = obj[key];
                      delete obj[key];
                      obj[key.replace(/\s+/g,'_').replace(/-/g,'').toLowerCase()] = value;
                      convert_keys(value);
                    });
                }
            };
            convert_keys(p);

            const errors = [];

            if ( !p.last_updated.getTime ) {
                errors.push("last updated");
            }
            p.last_updated = {
                key: zero_pad( p.last_updated.getTime() - new Date(1970, 0, 1).getTime(), 15 ),
                value: [
                    zero_pad(p.last_updated.getFullYear()),
                    zero_pad(p.last_updated.getMonth()+1),
                    zero_pad(p.last_updated.getDate()),
                ].join('-'),
            };

            if ( source == 'specialists' ) {

                if ( !valid_specialist_types[p.specialist_type] ) errors.push("specialist type");

                if ( !valid_referral_types[p.referral_type] ) errors.push("referral type");

                if ( !valid_procedure_types[p.procedure_type] ) errors.push("procedure type");

                p.locations.forEach( location => {
                    location.address = location.address.replace(/\s*$/,'');
                    location.map_url = `https://maps.google.com/maps/@${location.gps_coordinates.replace(/\s/g,'')},19z`;
                    location.gps_coordinates = location.gps_coordinates.split(/\s*,\s*/);
                });

            }

            ['forms','reports'].forEach( fr_key =>
                (p[fr_key]||[]).forEach( fr => {
                    fr.display_name = p.name + ( fr.name ? ': '+fr.name : '' );
                    fr.page_duration = {
                        key  : to_duration(fr.page_duration),
                        value: fr.page_duration,
                    };
                    fr.start_time = {
                        key  : to_time(fr.start_time),
                        value: fr.start_time
                    };
                    fr.thumb.replace(/^\/resources\/(thumbs\/.*)/, async (_,thumb) => {
                        thumb = __filename.replace(/[^\/]*$/,thumb);
                        if ( !fs.existsSync(thumb) ) {
                            console.log(`Creating thumb: ${fr.url} -> ${thumb}`);
                            const create_thumb =
                                  pdf => {
                                      let format;
                                      thumb.replace(/\.([a-z0-9]+)$/, (_,f) => format = f);
                                      const writer = child_process.spawn(
                                          '/bin/sh',[
                                              '-c',
                                              `pdftoppm -f 1 -l 1 - | convert -resize 200 - ${format}:-`,
                                          ]
                                      );
                                      writer.stdin.write(pdf);
                                      writer.stdin.end();
                                      let jpg = [];
                                      writer.stdout.on('data', data => jpg.push(data));
                                      writer.on(
                                          'close',
                                          () => fs.writeFileSync( thumb, Buffer.concat(jpg) )
                                      );
                                  };
                            if ( !fr.url.search(/^\/resources\//) ) { // local file
                                fr.url.replace(
                                    /^\/resources\/(.*)/,
                                    (_,source) => create_thumb(fs.readFileSync(
                                        __filename.replace(/[^\/]*$/,source)
                                    ))
                                );
                            } else {
                                ( fr.url.search(/^https:/) ? http : https )
                                    .get(
                                        fr.url,
                                        res => {
                                            let pdf = [];
                                            res
                                                .on( 'data', chunk => pdf.push(chunk) )
                                                .on( 'end' , () => create_thumb(Buffer.concat(pdf)) )
                                        }
                                    );
                            }
                        }
                    });
                })
            );

            if ( errors.length ) {
                throw Error(`Invalid keys(s): ${JSON.stringify(errors)}\nObject: ${JSON.stringify(p)}`);
            }

            return p;

        })

        // Sort:
        .sort( (a,b) =>
            a.name_key.localeCompare(b.name_key, {ignorePunctuation: true})
        )

    );

    output[source] = { records };

});

output.specialists.valid_values = {
    'specialist type': valid_specialist_types,
    'referral type'  : valid_referral_types,
    'procedure type' : valid_procedure_types,
};

fs.writeFileSync(
    __filename.replace(/[^\/]*$/,`entities.json`),
    JSON.stringify(output)
);

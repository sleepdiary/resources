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
    direct: 'a specialist who accepts referrals directly from members of the public',
    'secondary': 'a specialist who accepts referrals from any doctor (e.g. a general practitioner or primary care physician)',
    tertiary: 'a specialist who accepts referrals from other sleep specialists',
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
    if ( d == "variable" ) return 0;
    d.replace(
        /^([0-9]+) (day|week|month)s?$/i,
        (_,base,multiplier) => ret = parseInt(base,10) * multipliers[multiplier.toLowerCase()]
    );
    if ( !ret ) {
        throw Error(`Could not convert '${d}' to duration`);
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

if ( !fs.existsSync("thumbs") ) fs.mkdirSync("thumbs");

fs.cpSync(`software-thumbs`, `thumbs`, {recursive:true});

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

                if ( p.hasOwnProperty('referral_type') ) {
                    if ( !Array.isArray(p.referral_type) ) {
                        p.referral_type = [p.referral_type];
                    }
                    p.locations.forEach(
                        l => l.referral_type = l.referral_type || p.referral_type
                    );
                } else {
                    const known_referral_types = {}
                    const referral_types = p.referral_type = [];
                    p.locations.forEach(
                        l => {
                            if ( !l.referral_type ) {
                                errors.push(`missing referral_type for ${l}`);
                            }
                            if ( !Array.isArray(l.referral_type) ) {
                                l.referral_type = [l.referral_type];
                            }
                            l.referral_type.forEach(
                                t => {
                                    if ( !known_referral_types[t] ) {
                                        known_referral_types[t] = 1;
                                        referral_types.push(t);
                                    }
                                }
                            );
                        }
                    );
                }
                p.referral_type.forEach(
                    type => {
                        if ( !valid_referral_types[type] ) errors.push("referral type");
                    }
                );

                if ( !valid_procedure_types[p.procedure_type] ) errors.push("procedure type");

                p.locations.forEach( location => {
                    location.address = location.address.replace(/\s*$/,'');
                    location.map_url = `https://maps.google.com/maps/@${location.gps_coordinates.replace(/\s/g,'')},19z`;
                    location.gps_coordinates = location.gps_coordinates.split(/\s*,\s*/);
                });

            }

            const has_multiple_galleries = (p.forms||[]).length + (p.reports||[]).length > 1;
            ['forms','reports'].forEach( fr_key =>
                (p[fr_key]||[]).forEach( fr => {

                    if ( fr.name ) {
                        fr.display_name = p.name + ': ' + fr.name;
                        fr.short_name   = fr.name;
                    } else {
                        fr.display_name = fr.short_name = p.name;
                        if ( p[fr_key].length > 1 ) {
                            errors.push(`Please provide names for all ${fr} in ${p.name}`);
                        }
                    }
                    fr.display_name = fr.display_name.replace( /^the +/i, '' );
                    fr.short_name   = fr.short_name  .replace( /^the +/i, '' );

                    if ( fr.start_page ) {
                        fr.display_name += ",\npage "+fr.start_page;
                        fr.short_name   += ",\npage "+fr.start_page;
                    } else {
                        fr.start_page = 1;
                    }

                    if ( fr.layout == "calendar" ) {
                        fr.page_duration = {
                            key  : to_duration(fr.page_duration),
                            value: fr.page_duration,
                        };
                        fr.start_time = {
                            key  : to_time(fr.start_time),
                            value: fr.start_time
                        };
                    }

                    let thumbs = {};
                    if ( fr.thumb ) thumbs[fr.thumb] = [ 200, fr.url ];
                    fr.gallery.forEach( image => {
                        if ( fr.start_page != 1 && image.url.search(/#/) == -1 ) {
                            image.url += `#page=${fr.start_page}`
                        }
                        if ( !fr.url   ) fr.url   = image.url  ;
                        if ( !fr.thumb ) fr.thumb = image.thumb;
                        if ( !image.title ) image.title = fr.name || p.name;
                        image.display_name = ( has_multiple_galleries ? fr.name + ': ' : '' ) + image.title;
                        image.short_name = image.title;
                        image.short_name = image.short_name.replace( /^the +/i, '' );
                        thumbs[image.thumb] = [ 150, image.url ];
                    });
                    Object.keys(thumbs).forEach(
                        orig_thumb => orig_thumb.replace(
                            /^\/resources\/(thumbs\/.*)/,
                            async (_,thumb) => {
                                thumb = __filename.replace(/[^\/]*$/,thumb);
                                if ( !fs.existsSync(thumb) ) {
                                    const thumb_dir = thumb.replace(/\/[^/]*$/,'');
                                    if ( !fs.existsSync(thumb_dir) ) fs.mkdirSync(thumb_dir);
                                    const width = thumbs[orig_thumb][0];
                                    const url = thumbs[orig_thumb][1];
                                    console.log(`Creating thumb: ${url} -> ${thumb}`);
                                    const create_thumb =
                                          pdf => {
                                              let format;
                                              thumb.replace(/\.([a-z0-9]+)$/, (_,f) => format = f);
                                              const writer = child_process.spawn(
                                                  '/bin/sh',[
                                                      '-c',
                                                      `pdftoppm -f ${fr.start_page} -l ${fr.start_page} - | convert -resize ${width} - ${format}:-`,
                                                  ]
                                              );
                                              writer.stderr.on('data', data => console.error(`${data}`));
                                              writer.stdin.write(pdf);
                                              writer.stdin.end();
                                              let jpg = [];
                                              writer.stdout.on('data', data => jpg.push(data));
                                              writer.on(
                                                  'close',
                                                  () => fs.writeFileSync( thumb, Buffer.concat(jpg) )
                                              );
                                          };
                                    if ( !url.search(/^\/resources\//) ) { // local file
                                        url.replace(
                                            /^\/resources\/(.*)/,
                                            (_,source) => create_thumb(fs.readFileSync(
                                                __filename.replace(/[^\/]*$/,source)
                                            ))
                                        );
                                    } else {
                                        ( url.search(/^https:/) ? http : https )
                                            .get(
                                                url,
                                                res => {
                                                    let pdf = [];
                                                    res
                                                        .on( 'data', chunk => pdf.push(chunk) )
                                                        .on( 'end' , () => create_thumb(Buffer.concat(pdf)) )
                                                }
                                            );
                                    }
                                }
                            })
                    );

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

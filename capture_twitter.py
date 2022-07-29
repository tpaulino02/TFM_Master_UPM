import os, json, sys, datetime

def main(argv):
    
    now = '2022-05-25'
    yesterday = '2022-05-26'

    with open('config/hashtags.json', 'r') as myfile:
        obj = json.loads(myfile.read())

    narr = argv[2] if len(argv) > 2 else None
    ide = argv[3] if len(argv) > 3 else None

    if narr is not None and ide is not None:

        narrative = obj[narr]
        ideology = ide.replace('_', ' ')

        for hashtag in narrative[ideology]:
            os.system(
                '''
                python -m luigi --module workflow StoreTask --after {after} --before {before} \
                --source twitter \
                --gsicrawler-params '{{"query": "#{hashtag}", "library": "snscrape"}}' \
                --algorithms '["liwc", "mft"]' \
                --ideology \
                --geo
                '''.format(
                    hashtag=hashtag,
                    after=now,
                    before=yesterday
                )
            )

    else:
        for narrative in obj.values():
            for ideology in narrative.values():
                for hashtag in ideology:
                    os.system(
                        '''
                        python -m luigi --module workflow StoreTask --after {after} --before {before} \
                        --source twitter \
                        --gsicrawler-params '{{"query": \"#{hashtag}\", "library": "snscrape"}}' \
                        --algorithms '["liwc", "mft"]' \
                        --ideology \
                        --geo
                        '''.format(
                            hashtag=hashtag,
                            after=now,
                            before=yesterday
                        )
                    )
                    

if __name__ == "__main__":
   main(sys.argv[1:])

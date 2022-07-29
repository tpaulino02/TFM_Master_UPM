import os, json, sys, datetime

def main(argv):
    
    now = datetime.datetime.now()
    yesterday = (now - datetime.timedelta(days=1))

    with open('config/subreddits.json', 'r') as myfile:
        obj = json.loads(myfile.read())

    narr = argv[2] if len(argv) > 2 else None
    ide = argv[3] if len(argv) > 3 else None

    if narr is not None and ide is not None:

        narrative = obj[narr]
        ideology = ide.replace('_', ' ')

        for subreddit in narrative[ideology]:
            os.system(
                '''
                python -m luigi --module workflow StoreTask --after {after} --before {before} \
                --source reddit \
                --gsicrawler-params '{{"subreddit": "{subreddit}", "number": 4000}}' \
                --algorithms '["liwc", "mft"]' \
                --ideology \
                '''.format(
                    subreddit=subreddit,
                    after=yesterday.strftime("%Y-%m-%d"),
                    before=now.strftime("%Y-%m-%d")
                )
            )

    else:
        for narrative in obj.values():
            for ideology in narrative.values():
                for subreddit in ideology:
                    os.system(
                        '''
                        python -m luigi --module workflow StoreTask --after {after} --before {before} \
                        --source reddit \
                        --gsicrawler-params '{{"subreddit": \"{subreddit}\", "number": 4000}}' \
                        --algorithms '["liwc", "mft"]' \
                        --ideology \
                        '''.format(
                            subreddit=subreddit,
                            after=yesterday.strftime("%Y-%m-%d"),
                            before=now.strftime("%Y-%m-%d")
                        )
                    )
                    

if __name__ == "__main__":
   main(sys.argv[1:])

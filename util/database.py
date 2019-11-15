import asyncio
import datetime

import pytz


class Database:

    def __init__(self, bot):
        self._bot = bot

        self.guilds = GuildManager(self)
        self.stats = StatsManager(bot, self)
        self.storage = StorageManager(self)

        self._connect()

    def _connect(self):
        from motor.motor_asyncio import AsyncIOMotorClient

        self._bot.logger.info('[DATABASE] Connecting to Database...')
        self._client = AsyncIOMotorClient(self._bot.cfg.get('Database.ConnectURI'))
        self._bot.logger.info('[DATABASE] Successfully connected to the database!')
        self._database = self._client[self._bot.cfg.get('Database.DatabaseName')]

        asyncio.get_event_loop().create_task(self._setup())

    async def _setup(self):
        if await self._is_setup():
            return
        self._bot.logger.info('[DATABASE] Setup Database...')
        requests = {
            'name': 'Requests',
            'score': 0
        }
        servers = {
            'name': 'Guilds',
            'score': 0,
            'highscore': 0
        }
        await self._database['Stats'].insert_many([requests, servers])

    async def _is_setup(self):
        db_filter = {
            'name': 'Requests'
        }
        return await self._database['Stats'].find_one(db_filter) is not None

    async def get_document(self, collection: str, key: str, value):
        db_filter = {
            key: value
        }
        return await self._database[collection].find_one(db_filter)

    def get_cursor_by_filter(self, collection: str, db_filter):
        return self._database[collection].find(db_filter)

    async def set_document_value(self, collection, filter_key, filer_value, key, value):
        document = await self.get_document(collection, filter_key, filer_value)
        document[key] = value
        db_filter = {
            filter_key: filer_value
        }
        update_operation = {
            "$set": document
        }
        await self._database[collection].update_one(db_filter, update_operation, upsert=False)

    async def set_document_full(self, collection, filter_key, filer_value, document):
        db_filter = {
            filter_key: filer_value
        }
        update_operation = {
            "$set": document
        }
        await self._database[collection].update_one(db_filter, update_operation, upsert=False)

    async def add_document(self, collection, document):
        await self._database[collection].insert_one(document)

    async def count_documents_by_filter(self, collection, db_filter):
        return await self._database[collection].count_documents(db_filter)

    # REFORMAT THE DATABASE                                          hopefully
    async def reformat_database(self):
        self._bot.logger.info('Start...')
        guilds = dict()
        collection = self._database['GuildData']
        cursor = collection.find({})
        async for document in cursor:
            g_id = str(document['guild_id'])
            if g_id in guilds:
                continue
            guilds[g_id] = document

        new_docs = list()

        for key, value in guilds.items():
            try:
                guild_doc = {
                    'guild_id': int(key),
                    'lang': value['lang'],
                    'premium': value['premium'],
                    'delete_invoke': value['delete_invoke'],
                    'disabled_ads': value['disabled_ads'],
                    'permissions_warn': value['permissions_warn'],
                }

            except Exception as ex:
                self._bot.logger.info('Error:')
                self._bot.logger.info('Server ID: ' + str(key))
                self._bot.logger.info('Last Status Info: ' + str(value['last_status_info']))
                self._bot.logger.info('Last Shop Info: ' + str(value['last_shop_info']))
                self._bot.logger.info('Last Challenge Info: ' + str(value['last_challenge_info']))
                self._bot.logger.info(' ')
                raise ex
            new_docs.append(guild_doc)

        await collection.delete_many({})
        await collection.insert_many(new_docs)

    async def backup_database(self):
        cursor = self._database['GuildData'].find({})
        guild_documents = list()
        async for doc in cursor:
            guild_documents.append(doc)
        await self._database['GuildData_Backup'].delete_many({})
        await self._database['GuildData_Backup'].insert_many(guild_documents)


class GuildManager:

    def __init__(self, database: Database):
        self.database = database
        self.collection_name = 'GuildData'

    async def exists(self, guild_id: int):
        return await self.database.get_document(self.collection_name, 'guild_id', guild_id) is not None

    async def add(self, guild_id: int):
        if await self.exists(guild_id):
            return

        guild_doc = {
            'guild_id': guild_id,
            'lang': 'en-EN',
            'premium': False,
            'delete_invoke': False,
            'disabled_ads': False,
            'permissions_warn': True,
            'setup': False,
            'counters': [],
            'log_channel': None
        }
        await self.database.add_document(self.collection_name, guild_doc)

    example_object = [
        {
            "type": "members",
            "cid": "1237867",
            "args": [None]
        },
    ]

    async def get_data(self, guild_id: int):
        if not await self.exists(guild_id):
            await self.add(guild_id)
        return await self.database.get_document(self.collection_name, 'guild_id', guild_id)

    async def set_value(self, guild_id: int, key: str, value):
        if not await self.exists(guild_id):
            await self.add(guild_id)
        cache_doc = await self.get_data(guild_id)
        cache_doc[key] = value
        await self.set_data(guild_id, cache_doc)

    async def set_data(self, guild_id: int, document):
        if not await self.exists(guild_id):
            await self.add(guild_id)
        await self.database.set_document_full(self.collection_name, 'guild_id', guild_id, document)

    def get_data_by_filter(self, db_filter):
        return self.database.get_cursor_by_filter(self.collection_name, db_filter)

    async def count_by_filter(self, db_filter):
        return await self.database.count_documents_by_filter(self.collection_name, db_filter)

    async def add_all(self):
        counter = 0
        for guild in self.database._bot.guilds:
            await self.add(guild)
            counter += 1
        self.database._bot.logger.info(f'[DATABASE] Adding {counter} Guilds to the database!')


class StatsManager:

    def __init__(self, bot, database: Database):
        self.bot = bot
        self._database = database

    async def add_stats_request(self):
        old = (await self._database.get_document('Stats', 'name', 'Requests'))['score']
        new = old + 1
        await self._database.set_document_value('Stats', 'name', 'Requests', 'score', new)

    async def get_requests(self):
        return (await self._database.get_document('Stats', 'name', 'Requests'))['score']

    async def set_guild_amount(self):
        curr_guild_amount = self._database._bot.utils.bot_stats.guilds()
        guild_document = await self._database.get_document('Stats', 'name', 'Guilds')
        old_guild_amount = guild_document['score']
        if curr_guild_amount == old_guild_amount:
            return
        await self._database.set_document_value('Stats', 'name', 'Guilds', 'score', curr_guild_amount)
        highscore = guild_document['highscore']
        if curr_guild_amount <= highscore:
            return
        await self._database.set_document_value('Stats', 'name', 'Guilds', 'highscore', curr_guild_amount)

    async def get_guild_max(self):
        return (await self._database.get_document('Stats', 'name', 'Guilds'))['highscore']

    async def set_daily_stats(self):
        current_date = datetime.datetime.now(pytz.timezone('UTC')).strftime('%Y-%m-%d')
        if await self._database.get_document('DailyStats', 'date', current_date):
            # Todays Stats Where recorded
            return
        stats_doc = {
            "date": current_date,
            "server_amount": self.bot.utils.bot_stats.guilds(),
            "av_user": float(f'{await self.bot.utils.bot_stats.average_user():.2f}'),
            "unique_user": await self.bot.utils.bot_stats.unique_users()
        }
        await self._database.add_document('DailyStats', stats_doc)


class StorageManager:

    def __init__(self, database: Database):
        self._database = database
        self._collection_name = 'Storage'

    async def exists(self, path):
        return await self._database.get_document(self._collection_name, 'path', path) is not None

    async def add(self, path):
        if await self.exists(path):
            return
        user_doc = {
            'path': path,
            'value': 'None',
        }
        await self._database.add_document(self._collection_name, user_doc)

    async def set(self, path, value):
        if not await self.exists(path):
            await self.add(path)
        await self._database.set_document_value(self._collection_name, 'path', path, 'value', value)

    async def get(self, path):
        if not await self.exists(path):
            await self.add(path)
        return (await self._database.get_document(self._collection_name, 'path', path))['value']

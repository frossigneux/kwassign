# -*- coding: utf-8 -*-
#
# Author: François Rossigneux <francois.rossigneux@inria.fr>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Republishes counters after setting the user_id field."""

import itertools

from oslo.config import cfg

from kwassign.openstack.common.rpc import dispatcher as rpc_dispatcher
from kwassign.openstack.common.rpc import service as rpc_service
from kwassign.openstack.common import context
from kwassign.openstack.common import log
from kwassign.openstack.common import rpc
import security

LOG = log.getLogger(__name__)

service_opts = [
    cfg.StrOpt('metering_secret',
               required=True,
               ),
    cfg.StrOpt('metering_topic',
               required=True,
               ),
]

cfg.CONF.register_opts(service_opts)


class Service(rpc_service.Service):

    def start(self):
        """Starts the service."""
        super(Service, self).start()
        admin_context = context.RequestContext('admin', 'admin', is_admin=True)
        # Does nothing but allows the service to run indefinitely
        self.tg.add_timer(600,
                          self.manager.periodic_tasks,
                          context=admin_context)

    def initialize_service_hook(self, service):
        """Consumers must be declared before consume_thread starts."""
        self.conn.create_worker(cfg.CONF.metering_topic,
                                rpc_dispatcher.RpcDispatcher([self]),
                                'kwassign')

    def record_metering_data(self, context, data):
        """This method is triggered when counters are sent."""
        # We may have received only one counter on the wire
        if not isinstance(data, list):
            data = [data]

        modified_meters = []
        for meter in data:
            LOG.info('metering data %s for %s @ %s: %s',
                     meter['counter_name'],
                     meter['resource_id'],
                     meter.get('timestamp', 'NO TIMESTAMP'),
                     meter['counter_volume'])
            if security.verify_signature(meter, cfg.CONF.metering_secret):
                if meter['project_id'] is None:
                    meter['project_id'] = self.get_project_id(
                        meter['resource_id'])
                    if meter['project_id']:
                        security.append_signature(meter,
                                                  cfg.CONF.metering_secret)
                        modified_meters.append(meter)
            else:
                LOG.warning(
                    'message signature invalid, discarding message: %r',
                    meter)

        if modified_meters:
            self.publish_counter(context,
                                 cfg.CONF.metering_topic,
                                 modified_meters)

    def get_project_id(self, resource_id):
        """Retrieves the tenant associated with the host."""
        # TODO
        return '860e12ab7bd04067927fc2b0655f0ff1'

    def publish_counter(self, context, topic, meters):
        """Publishes counters on the bus."""
        topic = cfg.CONF.metering_topic
        msg = {
            'method': 'record_metering_data',
            'version': '1.0',
            'args': {'data': meters},
        }
        LOG.debug('PUBLISH: %s', str(msg))
        rpc.cast(context, topic, msg)

        for meter_name, meter_list in itertools.groupby(
                sorted(meters, key=lambda m: m['counter_name']),
                lambda m: m['counter_name']):
            msg = {
                'method': 'record_metering_data',
                'version': '1.0',
                'args': {'data': list(meter_list)},
            }
            rpc.cast(context, topic + '.' + meter_name, msg)

    def periodic_tasks(self, context):
        """Does nothing."""
        pass

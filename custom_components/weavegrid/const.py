"""Constants for the WeaveGrid integration."""

from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "weavegrid"
LOGGER = logging.getLogger(__package__)

API_URL: Final = "https://charge.weavegrid.com/graphql"

QUERY_LOGIN: Final = """
mutation LoginDriver($email: String!, $password: String, $useMagicLink: Boolean) {
  login(emailAddress: $email, password: $password, useMagicLink: $useMagicLink) {
    isLoggedIn
    status
    user {
      userId
      utility {
        acronym
      }
    }
  }
}
"""

QUERY_DASHBOARD_DATA: Final = """
query DashboardData {
  viewer {
    id
    vehicles(includeArchivedRegistrations: true) {
      data {
        vehicleId
        displayName
        isActive
        isEvse
        oem {
          name
        }
        connectivityDetail {
          isActive
          isCharging
          isPluggedIn
          isHome
        }
      }
    }
  }
}
"""

QUERY_DEVICE_STATUS: Final = """
query DeviceStatusCard($vehicleId: String!) {
  viewer {
    id
    vehicles(vehicleId: $vehicleId, includeBatteryInfo: true) {
      data {
        vehicleId
        batteryStatus {
          currentSoc
        }
        mcPlanStatus {
          mcStatus
          planIsActive
          optimization
          readyByDttm
          chargeStartDttm
          milesAddedByReadyByTime
          socAtReadyByTime
        }
      }
    }
  }
}
"""

QUERY_CHARGE_AGGREGATES: Final = """
query ChargeEventAggregates(
  $vehicleId: String!,
  $startDttm: DateTime!,
  $endDttm: DateTime!,
  $limit: Int
) {
  viewer {
    vehicles(vehicleId: $vehicleId, includeArchivedRegistrations: true) {
      data {
        vehicleId
        chargeEvents(
          inclusiveStartDttm: $startDttm
          inclusiveEndDttm: $endDttm
          locationRelationshipTypes: [home_primary]
          limit: $limit
        ) {
          totalAggregates: aggregates(
            aggregateUnit: total
            exclusiveStartDttm: $startDttm
            exclusiveEndDttm: $endDttm
          ) {
            data {
              chargeCost
              energyDeliveredKwh
              smartScore
            }
          }
          dailyAggregates: aggregates(
            aggregateUnit: day
            exclusiveStartDttm: $startDttm
            exclusiveEndDttm: $endDttm
            limit: $limit
          ) {
            data {
              usageDate
              chargeCost
              energyDeliveredKwh
            }
          }
        }
      }
    }
  }
}
"""

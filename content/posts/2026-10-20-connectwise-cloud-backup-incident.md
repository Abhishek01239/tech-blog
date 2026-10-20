---
title: "ConnectWise Freezes Cloud Backup After M365 Identity Abuse"
date: 2026-10-20
draft: false
description: "ConnectWise paused Cloud Backup after application-identity abuse reached Microsoft 365 tenants; scheduled backups and restores remain unavailable to partners."
image: "/images/2026-10-20-connectwise-cloud-backup-incident.jpg"
tags: [ConnectWise, Microsoft 365, Cloud Backup, SkyKick, identity security, MSP security]
categories: [Cybersecurity, Cloud]
author: "TechPulse"
---
ConnectWise suspended Cloud Backup, SaaS Security and Cloud Management after unauthorized access to application identities associated with its Cloud Backup service, formerly SkyKick. As of the company’s Oct. 19 update, scheduled backups, access to affected archives, restores, monitoring and some administration functions remained unavailable, with no confirmed restoration time. [1]

## Disabling access does not reverse tenant changes

ConnectWise says it revoked certificates associated with affected application connections and disabled seven application identities on Oct. 17. Its technical guidance cautions that disabling an application stops new authentication through that connection but does not undo changes already made inside a customer’s Microsoft 365 tenant. Previously issued tokens may remain usable until they expire or are invalidated. [1] [2]

The company’s guide directs partners to review both their own tenants and customer tenants they manage. Suggested checks include sign-in and audit logs, application credentials and consent grants, directory roles, federation settings, mailbox forwarding rules and delegated access. ConnectWise advises keeping affected applications disabled while investigating rather than treating the service suspension itself as proof a tenant is clean. [2]

## Telemetry is not a final impact count

Security firm Huntress reported Graph-token activity from an application identity on Oct. 15 and said it had confirmed unauthorized sign-ins in 162 monitored tenants by the evening of Oct. 16. It also described activity in one tenant involving a directory-role assignment and attempted application-credential changes. These are Huntress observations, not a complete impact count from ConnectWise. [3]

The Hacker News later reported larger sign-in telemetry figures attributed to Huntress. Those numbers refer to observed tenant activity and should not be confused with a confirmed count of compromised customers. [5]

ConnectWise says its backup archives remain encrypted, isolated and preserved, and that it has not found evidence they were accessed. That statement concerns the stored backup archives; it does not establish the security status of each live Microsoft 365 tenant. The company says it cannot independently inspect all downstream customer environments. [1] [2] [4]

For affected organizations, the incident creates both an investigation burden and a backup-and-restore gap. The clearest status as of Oct. 20 is that affected services remain suspended while partners are asked to investigate their own and managed tenants; restoration timing and the full downstream scope remain unresolved. [1] [2]

### Sources
[1] [ConnectWise Trust Center: Cloud Backup service interruption](https://www.connectwise.com/company/trust/advisories)
[2] [ConnectWise technical investigation and remediation guide](https://www.connectwise.com/contentassets/10777cd3364d440c86ed5270a94a5f24/connectwise-cloud-backup-technical-investigation-and-remediation-guide-1.pdf)
[3] [Huntress: ConnectWise vendor credential enables unauthorized access](https://www.huntress.com/blog/vendor-credential-enables-unauthorized-access)
[4] [Recorded Future News: ConnectWise suspends Cloud Backup after supply-chain attack](https://therecord.media/connectwise-suspends-cloud-backup-service-supply-chain-attack)
[5] [The Hacker News: ConnectWise suspends Cloud Backup after Microsoft 365 tenant activity](https://thehackernews.com/2026/10/connectwise-suspends-cloud-backup-after.html)

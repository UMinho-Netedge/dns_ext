# DNS Service

DNS Service is part of NetEdge-MEP micro-service architecture [[1]](#1).

The NetEdge-MEP is a CNF-based ETSI-MEC compliant MEP. NetEdge-MEP is part of NetEdge project, for more information on NetEdge, please check https://www.netedge.pt/

The DNS Service provides service discovery by name, to access services produced and registered by MEC Apps. This service is composed of a DNS API that configures a CoreDNS server. The DNS API Server implements a REST API with POST and DELETE methods using the ETSI GS MEC 011 DNSRule data type, which contains a rule id, the domain name, IP Address type, IP address and a Time-to-live (TTL), allowing an easy way to configure the CoreDNS Server dynamically.

For more information on NetEdge-MEP check: https://github.com/UMinho-Netedge/NetEdge-MEP/

## References
<a id="1">[1]</a>
Ferreira, V., Bastos, J., Martins, A., Araújo, P., Lori, N., Faria, J., Costa, A., López, H. (2023).
NETEDGE MEP: A CNF-based Multi-access Edge Computing Platform. 
ISCC 2023 Proceedings. (Accepted)
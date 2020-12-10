Instructions for changing a Load Balancer to use HTTPS

1) Deploy the stack using Cloudformation
2) Find the Load Balancer for the stack at https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#LoadBalancers:sort=loadBalancerName
3) Select the checkbox for the Load Balancer and check on the Listeners tab in the box at the bottom
4) Click "Add listener"
5) Select HTTPS 443
6) Select "+ Add action" -> Forward to -> <stackname>-dummyTarget
7) Select "From ACM" and "apt.ds.io - ..." under Default SSL Certificate
8) Hit Save in the upper right and then the Back arrow next to Listeners in the upper left
9) Back at the bottom, select view/edit rules under the entry you just created
10) Click the + button then "+ Insert Rule"
11) Add the following rules making sure they end up in this order:
 - IF Path is /saml/* THEN Forward to <stackname>-tg-fastapi
 - IF Path is /fastapi/* THEN Forward to <stackname>-tg-fastapi
 - IF Path is /* THEN Forward to <stackname>-tg-pgr
 12) Go back to the list of  Listeners and then to the HTTP 80 view/edit rules Remove all but the dummy rule
 13) Have Olaf or someone with Route53 Permissions move apt.ds.io (or setup a new domain) to point to that load balancer
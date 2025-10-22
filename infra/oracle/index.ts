import * as pulumi from "@pulumi/pulumi";
import * as oci from "@pulumi/oci";

// Import configuration
const config = new pulumi.Config();
const compartmentId = config.require("compartmentId");
const availabilityDomain = config.require("availabilityDomain");

// Create a Virtual Cloud Network
const vcn = new oci.core.VirtualNetwork("opendiscourse-vcn", {
    cidrBlocks: ["10.0.0.0/16"],
    compartmentId: compartmentId,
    displayName: "opendiscourse-vcn",
    dnsLabel: "opendiscourse"
});

// Create Internet Gateway
const internetGateway = new oci.core.InternetGateway("opendiscourse-ig", {
    compartmentId: compartmentId,
    vcnId: vcn.id,
    displayName: "opendiscourse-ig"
});

// Create Route Table
const routeTable = new oci.core.RouteTable("opendiscourse-rt", {
    compartmentId: compartmentId,
    vcnId: vcn.id,
    displayName: "opendiscourse-rt",
    routeRules: [{
        destination: "0.0.0.0/0",
        destinationType: "CIDR_BLOCK",
        networkEntityId: internetGateway.id
    }]
});

// Create Security List for HTTP/HTTPS
const securityList = new oci.core.SecurityList("opendiscourse-sl", {
    compartmentId: compartmentId,
    vcnId: vcn.id,
    displayName: "opendiscourse-sl",
    egressSecurityRules: [{
        destination: "0.0.0.0/0",
        destinationType: "CIDR_BLOCK",
        protocol: "all"
    }],
    ingressSecurityRules: [
        {
            protocol: "6",
            source: "0.0.0.0/0",
            sourceType: "CIDR_BLOCK",
            tcpOptions: {
                max: 22,
                min: 22
            },
            description: "SSH"
        },
        {
            protocol: "6",
            source: "0.0.0.0/0",
            sourceType: "CIDR_BLOCK",
            tcpOptions: {
                max: 80,
                min: 80
            },
            description: "HTTP"
        },
        {
            protocol: "6",
            source: "0.0.0.0/0",
            sourceType: "CIDR_BLOCK",
            tcpOptions: {
                max: 443,
                min: 443
            },
            description: "HTTPS"
        }
    ]
});

// Create Subnets
const publicSubnet = new oci.core.Subnet("opendiscourse-public-subnet", {
    cidrBlock: "10.0.1.0/24",
    compartmentId: compartmentId,
    vcnId: vcn.id,
    availabilityDomain: availabilityDomain,
    displayName: "opendiscourse-public-subnet",
    dnsLabel: "public",
    routeTableId: routeTable.id,
    securityListIds: [securityList.id]
});

// Create Compute Instance (using Always Free tier shape)
const instance = new oci.core.Instance("opendiscourse-instance", {
    availabilityDomain: availabilityDomain,
    compartmentId: compartmentId,
    displayName: "opendiscourse-app",
    shape: "VM.Standard.E2.1.Micro",
    shapeConfig: {
        memoryInGbs: 1,
        ocpus: 1
    },
    createVnicDetails: {
        subnetId: publicSubnet.id,
        displayName: "opendiscourse-primary-vnic",
        assignPublicIp: true
    },
    sourceDetails: {
        sourceType: "image",
        imageId: "ocid1.image.oc1..aaaaaaaag2uyg22gy2p5vqv657446payxdnyk5vl6bv54s67q42bju6g25ja" // Oracle Linux 8
    },
    metadata: {
        "ssh_authorized_keys": config.require("sshPublicKey")
    }
});

// Create Block Storage Volume (Additional 15GB free tier storage)
const blockVolume = new oci.core.Volume("opendiscourse-volume", {
    availabilityDomain: availabilityDomain,
    compartmentId: compartmentId,
    displayName: "opendiscourse-data-volume",
    sizeInGbs: 15
});

// Attach Block Volume to Instance
const volumeAttachment = new oci.core.VolumeAttachment("opendiscourse-volume-attachment", {
    attachmentType: "paravirtualized",
    instanceId: instance.id,
    volumeId: blockVolume.id
});

// Export important values
export const instancePublicIp = instance.publicIp;
export const vcnId = vcn.id;
export const instanceId = instance.id;
export const volumeId = blockVolume.id;
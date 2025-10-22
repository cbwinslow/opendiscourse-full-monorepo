import * as pulumi from "@pulumi/pulumi";
import * as cloudflare from "@pulumi/cloudflare";

// Import configuration
const config = new pulumi.Config();
const accountId = config.require("accountId");
const zoneId = config.require("zoneId");

// Create R2 bucket for static assets
const r2Bucket = new cloudflare.R2Bucket("opendiscourse-r2", {
    accountId: accountId,
    name: "opendiscourse-assets"
});

// Create KV namespace for caching
const kvNamespace = new cloudflare.WorkersKvNamespace("opendiscourse-kv", {
    accountId: accountId,
    title: "opendiscourse-kv"
});

// Create D1 database
const d1Database = new cloudflare.D1Database("opendiscourse-d1", {
    accountId: accountId,
    name: "opendiscourse-db"
});

// Create Queue for background processing
const queue = new cloudflare.Queue("opendiscourse-queue", {
    accountId: accountId,
    name: "opendiscourse-processing-queue"
});

// Create Worker script for API
const apiWorker = new cloudflare.WorkerScript("opendiscourse-api", {
    accountId: accountId,
    name: "opendiscourse-api",
    content: `export default {
        async fetch(request, env) {
            return new Response("OpenDiscourse API Worker");
        }
    }`,
    kvNamespaceBindings: [{
        name: "KV",
        namespaceId: kvNamespace.id
    }],
    plainTextBindings: [{
        name: "D1_BINDING",
        text: d1Database.id
    }]
});

// Create Hyperdrive config for database connection
const hyperdrive = new cloudflare.Hyperdrive("opendiscourse-hyperdrive", {
    accountId: accountId,
    name: "opendiscourse-hyperdrive",
    origin: {
        host: config.require("databaseHost"),
        port: 5432,
        database: "opendiscourse",
        user: config.require("databaseUser")
    },
    password: config.requireSecret("databasePassword")
});

// Export important values
export const r2BucketName = r2Bucket.name;
export const kvNamespaceId = kvNamespace.id;
export const d1DatabaseId = d1Database.id;
export const queueId = queue.id;
export const hyperdriveId = hyperdrive.id;
export const workerUrl = apiWorker.id.apply(id => `https://${id}.${accountId}.workers.dev`);
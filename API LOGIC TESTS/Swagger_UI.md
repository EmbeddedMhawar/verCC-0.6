Guardian
 3.3.0-rc 
OAS 3.0
The Managed Guardian Service (MGS) enables applications a way to mint emissions & carbon offset tokens without worrying about the complexities of managing the technology infrastructure. The MGS manages all of the technology infrastructure components so that companies that create applications for policies, emissions reporting, and the creation of offsets & credits can focus on what they do best.

API developer - Website
Send email to API developer
Apache 2.0
Servers

/api/v1 - version 1.0

Authorize
accounts


GET
/accounts/session
Returns current session of the user.



POST
/accounts/register
Registers a new user account.


POST
/accounts/login
Logs user into the system.


POST
/accounts/change-password
Change user password.



POST
/accounts/access-token
Returns access token.


GET
/accounts
Returns a list of users, excluding Standard Registry and Auditors.



GET
/accounts/standard-registries
Returns all Standard Registries.



GET
/accounts/standard-registries/aggregated
Returns all Standard Registries aggregated with polices and vcDocuments.



GET
/accounts/balance
Returns user's Hedera account balance.



PUT
/accounts/reset-password
Request password reset.


POST
/accounts/reset-password
Set new password.


GET
/accounts/terms/agree
Get current version of Terms of Use.



POST
/accounts/terms/agree
Accept Terms of Use.



POST
/accounts/sso/generate
Generate API token for Indexer.



POST
/accounts/loginByEmail
Log in user into the system.


GET
/accounts/usergroup



POST
/accounts/usergroup/login



POST
/accounts/otp/generate



POST
/accounts/otp/confirm



GET
/accounts/otp/status



POST
/accounts/otp/deactivate


analytics

artifacts


GET
/artifacts
Returns all artifacts.



POST
/artifacts/{parentId}
Upload artifact.



DELETE
/artifacts/{artifactId}
Delete artifact.


contracts


GET
/contracts
Return a list of all contracts.



POST
/contracts
Create contract.



POST
/contracts/import
Import contract.



GET
/contracts/{contractId}/permissions
Get contract permissions.



DELETE
/contracts/{contractId}
Remove contract.



GET
/contracts/wipe/requests
Return a list of all wipe requests.



POST
/contracts/wipe/{contractId}/requests/enable
Enable wipe requests.



POST
/contracts/wipe/{contractId}/requests/disable
Disable wipe requests.



POST
/contracts/wipe/requests/{requestId}/approve
Approve wipe request.



DELETE
/contracts/wipe/requests/{requestId}/reject
Reject wipe request.



DELETE
/contracts/wipe/{contractId}/requests
Clear wipe requests.



DELETE
/contracts/wipe/{contractId}/requests/{hederaId}
Clear wipe requests for hedera account.



POST
/contracts/wipe/{contractId}/admin/{hederaId}
Add wipe admin.



DELETE
/contracts/wipe/{contractId}/admin/{hederaId}
Remove wipe admin.



POST
/contracts/wipe/{contractId}/manager/{hederaId}
Add wipe manager.



DELETE
/contracts/wipe/{contractId}/manager/{hederaId}
Remove wipe manager.



POST
/contracts/wipe/{contractId}/wiper/{hederaId}
Add wipe wiper.



DELETE
/contracts/wipe/{contractId}/wiper/{hederaId}
Remove wipe wiper.



POST
/contracts/wipe/{contractId}/wiper/{hederaId}/{tokenId}
Add wipe wiper for token.



DELETE
/contracts/wipe/{contractId}/wiper/{hederaId}/{tokenId}
Remove wipe wiper for token.



POST
/contracts/retire/{contractId}/pools/sync
Sync retire pools.



GET
/contracts/retire/requests
Return a list of all retire requests.



GET
/contracts/retire/pools
Return a list of all retire pools.



DELETE
/contracts/retire/{contractId}/requests
Clear retire requests.



DELETE
/contracts/retire/{contractId}/pools
Clear retire pools.



POST
/contracts/retire/{contractId}/pools
Set retire pool.



DELETE
/contracts/retire/pools/{poolId}
Unset retire pool.



DELETE
/contracts/retire/requests/{requestId}
Unset retire request.



POST
/contracts/retire/pools/{poolId}/retire
Retire tokens.



POST
/contracts/retire/requests/{requestId}/approve
Approve retire request.



DELETE
/contracts/retire/requests/{requestId}/cancel
Cancel retire request.



POST
/contracts/retire/{contractId}/admin/{hederaId}
Add retire admin.



DELETE
/contracts/retire/{contractId}/admin/{hederaId}
Remove wipe admin.



GET
/contracts/retire
Return a list of all retire vcs.



GET
/contracts/retireIndexer
Return a list of all retire vcs from Indexer.


external


POST
/external/{policyId}/{blockTag}
Sends data from an external source.


POST
/external
Sends data from an external source.

ipfs


POST
/ipfs/file
Add file from ipfs.



POST
/ipfs/file/dry-run/{policyId}
Add file from ipfs for dry run mode.



GET
/ipfs/file/{cid}
Get file from ipfs.



GET
/ipfs/file/{cid}/dry-run
Get file from ipfs for dry run mode.


logs


POST
/logs
Return a list of all logs.



GET
/logs/attributes
Return a list of attributes.



GET
/logs/seq
Return url on seq store.



POST
/logs/tenant/{tenantId}


map


GET
/map/sh
Get sentinel API key.


metrics


GET
/metrics

modules


POST
/modules
Creates a new module.



GET
/modules
Return a list of all modules.



GET
/modules/schemas
Return a list of all module schemas.



POST
/modules/schemas
Creates a new module schema.



DELETE
/modules/{uuid}
Deletes the module.



GET
/modules/{uuid}
Retrieves module configuration.



PUT
/modules/{uuid}
Updates module configuration.



GET
/modules/menu
Return a list of modules.



GET
/modules/{uuid}/export/file
Return module and its artifacts in a zip file format for the specified module.



GET
/modules/{uuid}/export/message
Return Heder message ID for the specified published module.



POST
/modules/import/message
Imports new module from IPFS.



POST
/modules/import/file
Imports new module from a zip file.



POST
/modules/import/message/preview
Imports new module from IPFS.



POST
/modules/import/file/preview
Imports new module from a zip file.



PUT
/modules/{uuid}/publish
Publishes the module onto IPFS.



POST
/modules/validate
Validates selected module.


tools


POST
/tools
Creates a new tool.



GET
/tools
Return a list of all tools.



POST
/tools/push
Creates a new tool.



DELETE
/tools/{id}
Deletes the tool with the provided tool ID. Only users with the Standard Registry role are allowed to make the request.



GET
/tools/{id}
Retrieves tool configuration.



PUT
/tools/{id}
Updates tool configuration.



PUT
/tools/{id}/publish
Publishes the tool onto IPFS.



PUT
/tools/{id}/push/publish
Publishes the tool onto IPFS.



POST
/tools/validate
Validates selected tool.



GET
/tools/{id}/export/file
Return tool and its artifacts in a zip file format for the specified tool.



GET
/tools/{id}/export/message
Return Heder message ID for the specified published tool.



POST
/tools/import/message/preview
Imports new tool from IPFS.



POST
/tools/import/message
Imports new tool from IPFS.



POST
/tools/import/file/preview
Imports new tool from a zip file.



POST
/tools/import/file
Imports new tool from a zip file.



POST
/tools/import/file-metadata
Imports new tool from a zip file.



POST
/tools/push/import/file
Imports new tool from a zip file.



POST
/tools/push/import/file-metadata
Imports new tool from a zip file.



POST
/tools/push/import/message
Imports new tool from IPFS.



GET
/tools/menu/all
Return a list of tools.



GET
/tools/check/{messageId}
Checks the availability of the tool.


profiles


GET
/profiles/{username}
Returns user account info.



PUT
/profiles/{username}
Sets Hedera credentials for the user.



PUT
/profiles/push/{username}
Sets Hedera credentials for the user.



GET
/profiles/{username}/balance
Returns user's Hedera account balance.



PUT
/profiles/restore/{username}
Restore user data (policy, DID documents, VC documents).



PUT
/profiles/restore/topics/{username}
List of available recovery topics.



POST
/profiles/did-document/validate
Validate DID document format.



POST
/profiles/did-keys/validate
Validate DID document keys.



GET
/profiles/keys
Returns the list of existing keys.



POST
/profiles/keys
Creates a new key.



DELETE
/profiles/keys/{id}
Deletes the key.



POST
/profiles/permissions-map
Add mapped permissions to the organization



GET
/profiles/permissions-map/organizations
Returns organizations list.



GET
/profiles/permissions-map/{orgName}
Returns mapped permissions by organization.



POST
/profiles/vault/set


policies


GET
/policies
Return a list of all policies.



POST
/policies
Creates a new policy.



POST
/policies/migrate-data
Migrate policy data.



POST
/policies/push/migrate-data
Migrate policy data asynchronous.



POST
/policies/push
Creates a new policy.



POST
/policies/push/{policyId}
Clones policy.



DELETE
/policies/push/{policyId}
Remove policy.



GET
/policies/{policyId}
Retrieves policy configuration.



PUT
/policies/{policyId}
Updates policy configuration.



PUT
/policies/{policyId}/publish
Publishes the policy onto IPFS.



PUT
/policies/push/{policyId}/publish
Publishes the policy onto IPFS.



PUT
/policies/{policyId}/dry-run
Dry Run policy.



PUT
/policies/{policyId}/discontinue
Discontinue policy.



PUT
/policies/{policyId}/draft
Return policy to editing.



POST
/policies/validate
Validates policy.



GET
/policies/{policyId}/navigation
Returns a policy navigation.



GET
/policies/{policyId}/groups
Returns a list of groups the user is a member of.



POST
/policies/{policyId}/groups
Makes the selected group active.



GET
/policies/{policyId}/documents
Get policy documents.



GET
/policies/{policyId}/search-documents
Get policy documents with filters.



GET
/policies/{policyId}/export-documents
Returns a zip file containing policy project data.



GET
/policies/{policyId}/document-owners
Get policy document owners.



GET
/policies/{policyId}/tokens
Get policy tokens.



GET
/policies/{policyId}/data
Get policy data.



POST
/policies/data
Upload policy data.



GET
/policies/{policyId}/virtual-keys
Get policy virtual keys.



POST
/policies/{policyId}/virtual-keys
Upload policy virtual keys.



GET
/policies/{policyId}/tag-block-map
Get policy tag block map.



GET
/policies/{policyId}/blocks
Retrieves data for the policy root block.



GET
/policies/{policyId}/blocks/{uuid}
Requests block data.



POST
/policies/{policyId}/blocks/{uuid}
Sends data to the specified block.



POST
/policies/{policyId}/tag/{tagName}/blocks
Sends data to the specified block.



GET
/policies/{policyId}/tag/{tagName}/blocks
Requests block data.



GET
/policies/{policyId}/tag/{tagName}
Requests block config.



GET
/policies/{policyId}/blocks/{uuid}/parents
Requests block's parents.



GET
/policies/blocks/about
Returns block descriptions.



GET
/policies/{policyId}/export/file
Return policy and its artifacts in a zip file format for the specified policy.



GET
/policies/{policyId}/export/message
Return Heder message ID for the specified published policy.



GET
/policies/{policyId}/export/xlsx
Return policy and its artifacts in a xlsx file format for the specified policy.



POST
/policies/import/message
Imports new policy from IPFS.



POST
/policies/push/import/message
Imports new policy from IPFS.



POST
/policies/import/message/preview
Policy preview from IPFS.



POST
/policies/push/import/message/preview
Policy preview from IPFS.



POST
/policies/import/file
Imports new policy from a zip file.



POST
/policies/import/file-metadata
Imports new policy from a zip file with metadata.



POST
/policies/push/import/file
Imports new policy from a zip file.



POST
/policies/push/import/file-metadata
Imports new policy from a zip file with metadata.



POST
/policies/import/file/preview
Policy preview from a zip file.



POST
/policies/import/xlsx
Imports new policy from a xlsx file.



POST
/policies/push/import/xlsx
Imports new policy from a xlsx file.



POST
/policies/import/xlsx/preview
Policy preview from a xlsx file.



GET
/policies/{policyId}/dry-run/users
Returns virtual users.



POST
/policies/{policyId}/dry-run/user
Creates virtual users.



POST
/policies/{policyId}/dry-run/login
Change active virtual user.



POST
/policies/{policyId}/dry-run/block
.



GET
/policies/{policyId}/dry-run/block/{tagName}/history
.



POST
/policies/{policyId}/savepoint/create
Create dry-run savepoint.



POST
/policies/{policyId}/savepoint/delete
Delete dry-run savepoint.



GET
/policies/{policyId}/savepoint/restore
Get savepoint state.



POST
/policies/{policyId}/savepoint/restore
Restore dry-run savepoint.



POST
/policies/{policyId}/dry-run/restart
Clear dry-run state.



GET
/policies/{policyId}/dry-run/transactions
Get dry-run details (Transactions).



GET
/policies/{policyId}/dry-run/artifacts
Get dry-run details (Artifacts).



GET
/policies/{policyId}/dry-run/ipfs
Get dry-run details (Files).



GET
/policies/{policyId}/multiple
Requests policy links.



POST
/policies/{policyId}/multiple
Creates policy link.



POST
/policies/{policyId}/test
Add policy test.



GET
/policies/{policyId}/test/{testId}
Get policy test.



DELETE
/policies/{policyId}/test/{testId}
Delete policy test.



POST
/policies/{policyId}/test/{testId}/start
Start policy test.



POST
/policies/{policyId}/test/{testId}/stop
Stop policy test.



GET
/policies/{policyId}/test/{testId}/details
Get test details.



GET
/policies/methodologies/categories
Get all categories


POST
/policies/methodologies/search
Get filtered policies



GET
/policies/opensourced
Get Opensourced policies list.



POST
/policies/opensourced/getByUrl
Get Opensourced policy file.



POST
/policies/push/opensourced/import
Import opensourced policy


schema


GET
/schema/{schemaId}
Returns schema by schema ID.



GET
/schema/{schemaId}/parents
Returns all parent schemas.



GET
/schema/{schemaId}/tree
Returns schema tree.


schemas


GET
/schemas
Return a list of all schemas.



PUT
/schemas
Updates the schema.



GET
/schemas/{topicId}
Return a list of all schemas.



POST
/schemas/{topicId}
Creates a new schema.



GET
/schemas/type/{schemaType}
Finds the schema using the json document type.



GET
/schemas/type-by-user/{schemaType}
Finds the schema using the json document type.



GET
/schemas/list/all
Returns a list of schemas.



GET
/schemas/list/sub
Returns a list of schemas.



GET
/schemas/schema-with-sub-schemas
Returns a list of schemas.



POST
/schemas/push/copy
Copy schema.



POST
/schemas/push/{topicId}
Creates a new schema.



DELETE
/schemas/{schemaId}
Deletes the schema with the provided schema ID.



PUT
/schemas/{schemaId}/publish
Publishes the schema with the provided schema ID.



PUT
/schemas/push/{schemaId}/publish
Publishes the schema with the provided schema ID.



POST
/schemas/import/message/preview
Previews the schema from IPFS without loading it into the local DB.



POST
/schemas/push/import/message/preview
Previews the schema from IPFS without loading it into the local DB.



POST
/schemas/import/file/preview
Previews the schema from a zip file.



POST
/schemas/{topicId}/import/message
Imports new schema from IPFS into the local DB.



POST
/schemas/push/{topicId}/import/message
Imports new schema from IPFS into the local DB.



POST
/schemas/{topicId}/import/file
Imports new schema from a zip file into the local DB.



POST
/schemas/push/{topicId}/import/file
Imports new schema from a zip file into the local DB.



GET
/schemas/{schemaId}/export/message
Returns Hedera message IDs of the published schemas.



GET
/schemas/{schemaId}/export/file
Returns schema files for the schema.



POST
/schemas/system/{username}
Creates a new system schema.



GET
/schemas/system/{username}
Return a list of all system schemas.



DELETE
/schemas/system/{schemaId}
Deletes the system schema with the provided schema ID.



PUT
/schemas/system/{schemaId}
Updates the system schema.



PUT
/schemas/system/{schemaId}/active
Makes the selected scheme active. Other schemes of the same type become inactive



GET
/schemas/system/entity/{schemaEntity}
Finds the schema using the schema type.



GET
/schemas/{schemaId}/export/xlsx
Return schemas in a xlsx file format for the specified policy.



POST
/schemas/{topicId}/import/xlsx
Imports new schema from a xlsx file into the local DB.



POST
/schemas/push/{topicId}/import/xlsx
Imports new schema from a xlsx file into the local DB.



POST
/schemas/import/xlsx/preview
Previews the schema from a xlsx file.



GET
/schemas/export/template
Returns a list of schemas.


settings


POST
/settings
Set settings.



GET
/settings
Returns current settings.



GET
/settings/environment
Returns current environment name.



GET
/settings/about
Returns package version.



POST
/settings/tenant/{tenantId}



GET
/settings/tenant/{tenantId}



GET
/settings/banner



POST
/settings/banner



GET
/settings/banner/obsolete



POST
/settings/banner/obsolete



POST
/settings/banner/obsolete/preview


tags


POST
/tags
Creates new tag.



POST
/tags/search
Search tags.



DELETE
/tags/{uuid}
Delete tag.



POST
/tags/synchronization
Synchronization of tags with an external network.



GET
/tags/schemas
Return a list of all tag schemas.



POST
/tags/schemas
Creates a new tag schema.



DELETE
/tags/schemas/{schemaId}
Deletes the schema.



PUT
/tags/schemas/{schemaId}
Updates schema configuration.



PUT
/tags/schemas/{schemaId}/publish
Publishes the schema.



GET
/tags/schemas/published
Return a list of all published schemas.


tasks


GET
/tasks/{taskId}
Returns task statuses by Id.


tokens


GET
/tokens
Return a list of tokens.



POST
/tokens
Creates a new token.



PUT
/tokens
Update token.



GET
/tokens/{tokenId}
Return a token by id.



POST
/tokens/push
Creates a new token.



PUT
/tokens/push
Update token.



DELETE
/tokens/push/{tokenId}
Deletes the token with the provided schema ID.



PUT
/tokens/{tokenId}/associate
Associates the user with the provided Hedera token.



PUT
/tokens/push/{tokenId}/associate
Associates the user with the provided Hedera token.



PUT
/tokens/{tokenId}/dissociate
Associate the user with the provided Hedera token.



PUT
/tokens/push/{tokenId}/dissociate
Associate the user with the provided Hedera token.



PUT
/tokens/{tokenId}/{username}/grant-kyc
Sets the KYC flag for the user.



PUT
/tokens/push/{tokenId}/{username}/grant-kyc
Sets the KYC flag for the user.



PUT
/tokens/{tokenId}/{username}/revoke-kyc
Unsets the KYC flag for the user.



PUT
/tokens/push/{tokenId}/{username}/revoke-kyc
Unsets the KYC flag for the user.



PUT
/tokens/{tokenId}/{username}/freeze
Freeze transfers of the specified token for the user.



PUT
/tokens/{tokenId}/{username}/unfreeze
Unfreezes transfers of the specified token for the user.



PUT
/tokens/push/{tokenId}/{username}/freeze
Freeze transfers of the specified token for the user.



PUT
/tokens/push/{tokenId}/{username}/unfreeze
Unfreezes transfers of the specified token for the user.



GET
/tokens/{tokenId}/{username}/info
Returns user information for the selected token.



GET
/tokens/{tokenId}/serials
Return token serials.



GET
/tokens/menu/all
Return a list of tokens.


themes


POST
/themes
Creates a new theme.



GET
/themes
Returns a list of all themes.



PUT
/themes/{themeId}
Updates theme configuration.



DELETE
/themes/{themeId}
Deletes the theme.



POST
/themes/import/file
Imports new theme from a zip file.



GET
/themes/{themeId}/export/file
Returns a zip file containing the theme.


trust-chains


GET
/trust-chains
Returns a list of all VP documents.



GET
/trust-chains/{hash}
Builds and returns a trustchain, from the VP to the root VC document.


wizard


POST
/wizard/policy
Creates a new policy.



POST
/wizard/push/policy
Creates a new policy.



POST
/wizard/{policyId}/config
Get policy config.


branding


POST
/branding
Update branding.



GET
/branding



POST
/branding/{tenantId}



GET
/branding/{tenantId}

suggestions


POST
/suggestions
Get next and nested suggested block types



POST
/suggestions/config
Set suggestions config



GET
/suggestions/config
Get suggestions config


notifications


GET
/notifications
Get all notifications



GET
/notifications/new
Get new notifications



GET
/notifications/progresses
Get progresses



POST
/notifications/read/all
Read all notifications



DELETE
/notifications/delete/{notificationId}
Delete notifications up to this point


projects


POST
/projects/search
Search projects


POST
/projects/compare/documents
Compare documents.


GET
/projects/properties
Get all properties

record


GET
/record/{policyId}/status
Get recording or running status.



POST
/record/{policyId}/recording/start
Start recording.



POST
/record/{policyId}/recording/stop
Stop recording.



GET
/record/{policyId}/recording/actions
Get recorded actions.



POST
/record/{policyId}/running/start
Run record from a zip file.



POST
/record/{policyId}/running/stop
Stop running.



GET
/record/{policyId}/running/results
Get running results.



GET
/record/{policyId}/running/details
Get running details.



POST
/record/{policyId}/running/fast-forward
Fast Forward.



POST
/record/{policyId}/running/retry
Retry step.



POST
/record/{policyId}/running/skip
Skip step.


ai-suggestions


GET
/ai-suggestions/ask
Get methodology suggestion



PUT
/ai-suggestions/rebuild-vector
Rebuild AI vector


permissions


GET
/permissions
Return a list of all permissions.



GET
/permissions/roles
Return a list of all roles.



POST
/permissions/roles
Creates new role.



PUT
/permissions/roles/{id}
Updates role configuration.



DELETE
/permissions/roles/{id}
Deletes the role.



POST
/permissions/roles/default
Set default role.



GET
/permissions/users
Return a list of all users.



GET
/permissions/users/{username}
Updates user permissions.



PUT
/permissions/users/{username}
Updates user permissions.



GET
/permissions/users/{username}/policies
Return a list of all roles.



POST
/permissions/users/{username}/policies/assign
Assign policy.



PUT
/permissions/users/{username}/delegate
Delegate user permissions.



POST
/permissions/users/{username}/policies/delegate
Delegate policy.


policy-statistics


POST
/policy-statistics
Creates a new statistic definition.



GET
/policy-statistics
Return a list of all statistic definitions.



GET
/policy-statistics/{definitionId}
Retrieves statistic definition.



PUT
/policy-statistics/{definitionId}
Updates statistic definition.



DELETE
/policy-statistics/{definitionId}
Deletes the statistic definition.



PUT
/policy-statistics/{definitionId}/publish
Publishes statistic definition.



GET
/policy-statistics/{definitionId}/relationships
Retrieves statistic relationships.



GET
/policy-statistics/{definitionId}/documents
Return a list of all documents.



POST
/policy-statistics/{definitionId}/assessment
Creates a new statistic assessment.



GET
/policy-statistics/{definitionId}/assessment
Return a list of all statistic assessment.



GET
/policy-statistics/{definitionId}/assessment/{assessmentId}
Retrieves statistic assessment.



GET
/policy-statistics/{definitionId}/assessment/{assessmentId}/relationships
Retrieves assessment relationships.



POST
/policy-statistics/{policyId}/import/file
Imports new statistic definition from a zip file.



GET
/policy-statistics/{definitionId}/export/file
Returns a zip file containing statistic definition.



POST
/policy-statistics/import/file/preview
Imports a zip file containing statistic definition.


schema-rules


POST
/schema-rules
Creates a new schema rule.



GET
/schema-rules
Return a list of all schema rules.



GET
/schema-rules/{ruleId}
Retrieves schema rule.



PUT
/schema-rules/{ruleId}
Updates schema rule.



DELETE
/schema-rules/{ruleId}
Deletes the schema rule.



PUT
/schema-rules/{ruleId}/activate
Activates schema rule.



PUT
/schema-rules/{ruleId}/inactivate
Inactivates schema rule.



GET
/schema-rules/{ruleId}/relationships
Retrieves schema rule relationships.



POST
/schema-rules/data



POST
/schema-rules/{policyId}/import/file
Imports new rules from a zip file.



GET
/schema-rules/{ruleId}/export/file
Returns a zip file containing rules.



POST
/schema-rules/import/file/preview
Imports a zip file containing rules.


formulas


POST
/formulas
Creates a new formula.



GET
/formulas
Return a list of all formulas.



GET
/formulas/{formulaId}
Retrieves formula.



PUT
/formulas/{formulaId}
Updates formula.



DELETE
/formulas/{formulaId}
Deletes the formula.



GET
/formulas/{formulaId}/relationships
Retrieves Formula relationships.



POST
/formulas/{policyId}/import/file
Imports new formula from a zip file.



GET
/formulas/{formulaId}/export/file
Returns a zip file containing formula.



POST
/formulas/import/file/preview
Imports a zip file containing formula.



PUT
/formulas/{formulaId}/publish
Publishes formula.



POST
/formulas/data


external-policies


GET
/external-policies
Returns the list of requests for adding remote policies.



POST
/external-policies/preview
Returns preview of the remote policies.



POST
/external-policies/import
Creates a request to import a remote policy.



POST
/external-policies/push/{messageId}/approve
Approves the request to import a remote policy, and imports it.



POST
/external-policies/push/{messageId}/reject
Rejects the request to import a remote policy.



POST
/external-policies/{messageId}/approve
Approves the request to import a remote policy, and imports it.



POST
/external-policies/{messageId}/reject
Rejects the request to import a remote policy.



GET
/external-policies/requests
Returns the list of requests for action from remote Guardians.



PUT
/external-policies/requests/{messageId}/approve
Approves a request for an action from a remote Guardian.



PUT
/external-policies/requests/{messageId}/reject
Rejects a request for an action from a remote Guardian



PUT
/external-policies/requests/{messageId}/cancel
Cancels a request for an action from a remote Guardian



PUT
/external-policies/requests/{messageId}/reload
Reloads a request for an action from a remote Guardian



GET
/external-policies/requests/count
Returns the count of entries in the list of requests for actions from remote Guardians.



GET
/external-policies/requests/document
Returns the request document by startMessageId.


policy-labels


POST
/policy-labels
Creates a new policy label.



GET
/policy-labels
Return a list of all policy labels.



GET
/policy-labels/{definitionId}
Retrieves policy label.



PUT
/policy-labels/{definitionId}
Updates policy label.



DELETE
/policy-labels/{definitionId}
Deletes the policy label.



PUT
/policy-labels/{definitionId}/publish
Publishes policy label.



PUT
/policy-labels/push/{definitionId}/publish
Publishes policy label.



GET
/policy-labels/{definitionId}/relationships
Retrieves policy label relationships.



POST
/policy-labels/{policyId}/import/file
Imports new labels from a zip file.



GET
/policy-labels/{definitionId}/export/file
Returns a zip file containing labels.



POST
/policy-labels/import/file/preview
Imports a zip file containing labels.



POST
/policy-labels/components
Search labels ans statistics.



GET
/policy-labels/{definitionId}/tokens
Return a list of all documents.



GET
/policy-labels/{definitionId}/tokens/{documentId}
Return a list of all documents.



POST
/policy-labels/{definitionId}/documents
Creates a new label document.



GET
/policy-labels/{definitionId}/documents
Return a list of all label documents.



GET
/policy-labels/{definitionId}/documents/{documentId}
Retrieves label document.



GET
/policy-labels/{definitionId}/documents/{documentId}/relationships
Retrieves documents relationships.


worker-tasks


GET
/worker-tasks
Get all worker tasks



POST
/worker-tasks/restart
Restart task



DELETE
/worker-tasks/delete/{taskId}
Delete task


download


GET
/download/invoice/{secureId}
Download invoice

tenants


POST
/tenants
Return Tenants. For Admin role only.



POST
/tenants/user
Return user Tenants. For Tenant Admin role only.



PUT
/tenants/user
Create New Tenant. For Tenant Admin role only.



POST
/tenants/delete
Delete Tenant and all related data



GET
/tenants/settings
Get Tenant related settings.



GET
/tenants/invite/{tenantId}/sr
Get posible Standard Registries for invite.



POST
/tenants/invite
Send Invite link for new User.



POST
/tenants/invite/delete
Delete Invite.



POST
/tenants/{tenantId}/users
Return users for Tenant.



POST
/tenants/{tenantId}/users-and-invites
Return users and invites for Tenant.



DELETE
/tenants/{tenantId}/users/{userId}
Delete Tenant user.



POST
/tenants/reorder
Reorder tenants



GET
/tenants/{tenantId}/azureb2c
Get tenant setting for Azure B2C



POST
/tenants/{tenantId}/azureb2c
Update tenant setting for Azure B2C



DELETE
/tenants/{tenantId}/azureb2c
Delete tenant setting for Azure B2C



Schemas
AccountsSessionResponseDTO
InternalServerErrorDTO
Response451_DTO
AccountsResponseDTO
RegisterUserDTO
LoginUserDTO
ChangePasswordDTO
ProofDTO
VcDTO
VpDTO
VcDocumentDTO
PolicyTestDTO
PolicyDTO
AggregatedDTOItem
UserAccountDTO
BalanceResponseDTO
CommonResultDTO
ResetPasswordRequestDTO
CommonValidatedResultDTO
ResetPasswordDTO
TermsVersionResponseDTO
SsoTokenResultDTO
UserInfo
MgsAccountsSessionResponseDTO
MgsLoginUserDTO
FilterSearchPoliciesDTO
SearchPolicyDTO
SearchPoliciesDTO
CompareFileDTO
FilterPolicyDTO
FilterPoliciesDTO
ComparePoliciesDTO
FilterModulesDTO
CompareModulesDTO
FilterSchemaDTO
FilterSchemasDTO
CompareSchemasDTO
FilterDocumentsDTO
CompareDocumentsDTO
FilterToolsDTO
CompareToolsDTO
FilterSearchBlocksDTO
SearchBlocksDTO
ArtifactDTOItem
ContractDTO
ContractConfigDTO
WiperRequestDTO
RetireRequestDTO
Date
RetirePoolDTO
RetirePoolTokenDTO
RetireRequestTokenDTO
ExternalDocumentDTO
LogFilterDTO
LogResultDTO
ModuleDTO
SchemaDTO
ExportMessageDTO
ImportMessageDTO
ModulePreviewDTO
BlockErrorsDTO
ValidationErrorsDTO
ModuleValidationDTO
BlockDTO
ToolDTO
TaskDTO
ToolValidationDTO
ToolPreviewDTO
ProfileDTO
SubjectDTO
DidDocumentDTO
DidKeyDTO
CredentialsDTO
DidDocumentStatusDTO
DidKeyStatusDTO
DidDocumentWithKeyDTO
PolicyKeyDTO
PolicyKeyConfigDTO
PermissionsMapDetailsDTO
PermissionsMapDTO
MigrationConfigPoliciesDTO
MigrationConfigDTO
PoliciesValidationDTO
PolicyVersionDTO
PolicyValidationDTO
Object
ServiceUnavailableErrorDTO
PolicyPreviewDTO
DebugBlockDataDTO
DebugBlockConfigDTO
DebugBlockResultDTO
DebugBlockHistoryDTO
RunningDetailsDTO
PolicyCategoryDTO
OpedSourcedPolicyDTO
VersionSchemaDTO
MessageSchemaDTO
ExportSchemaDTO
SystemSchemaDTO
SettingsDTO
BannerSettingsDto
TagDTO
TagFilterDTO
TagMapDTO
StatusDTO
TaskStatusDTO
TokenDTO
TokenInfoDTO
ThemeRoleDTO
ThemeDTO
VpDocumentDTO
WizardConfigDTO
WizardResultDTO
WizardConfigAsyncDTO
WizardPreviewDTO
BrandingDTO
SuggestionsInputDTO
SuggestionsOutputDTO
SuggestionsConfigItemDTO
SuggestionsConfigDTO
NotificationDTO
ProgressDTO
ProjectDTO
CompareDocumentsV2DTO
PropertiesDTO
RecordStatusDTO
RecordActionDTO
ResultInfoDTO
ResultDocumentDTO
RunningResultDTO
RoleDTO
PermissionsDTO
UserDTO
AssignPolicyDTO
StatisticDefinitionDTO
StatisticDefinitionRelationshipsDTO
StatisticAssessmentDTO
StatisticAssessmentRelationshipsDTO
SchemaRuleDTO
SchemaRuleRelationshipsDTO
SchemaRuleOptionsDTO
SchemaRuleDataDTO
FormulaDTO
FormulaRelationshipsDTO
FormulasDataDTO
FormulasOptionsDTO
ExternalPolicyDTO
PolicyRequestDTO
PolicyRequestCountDTO
PolicyLabelDTO
PolicyLabelRelationshipsDTO
PolicyLabelFiltersDTO
PolicyLabelComponentsDTO
PolicyLabelDocumentDTO
PolicyLabelDocumentRelationshipsDTO
WorkersTasksDTO
TenantsFilterDTO
TenantDTO
DeleteTenantRequestDTO
TenantInviteDTO
UsersFilterDTO
TenantsReorderDTO
AzureB2CDTO
CredentialSubjectDTO
RegisteredUsersDTO
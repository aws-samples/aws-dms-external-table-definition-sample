## Sample script to generate an external table definition when using Amazon S3 as source endpoint in AWS Database Migration Service (AWS DMS)
When configuring an Amazon S3 location as a source endpoint in AWS DMS, a JSON document defining the list of tables, columns and their data types is required.  Creating this JSON document manually for a large number of tables can be time consuming and error prone.  This sample utility automates the generation of this table definition by using a crawler in AWS Glue to discover the list of tables and columns.  The [CloudFormation template](cloudformation-templates/DMSS3TableDef.yaml) configures a crawler in AWS Glue, creates a database in the AWS Glue catalog and the related IAM roles.  The python [script](scripts/glue_def_extract.py) reads the schema from the database to generate a JSON document in the format required by AWS DMS.  This JSON document can then be used to configure an endpoint in AWS DMS.  

## Usage
1. Copy source files in comma-separated value (.csv) format to Amazon S3 and organize in a folder structure as required by AWS DMS, refer to [Using Amazon S3 as a Source for AWS DMS](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.S3.html). 
2. Launch the [CloudFormation template](cloudformation-templates/DMSS3TableDef.yaml) in your region, use lower case letters for the CloudFormation stack name since the database name is derived from this.  Once the stack completes, make a note of the database name and crawler name in the outputs tab
3. From the AWS Management Console, run the AWS Glue crawler and wait for the crawler to complete 
4. From the AWS Management Console, verify if tables have been created in the AWS Glue catalog.  If the desired tables were not created, configure the [crawler](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html) and re-run the crawler
5. Once the desired tables have been created by the AWS Glue crawler, run the python [script](scripts/glue_def_extract.py) to generate a JSON document with the table definitions
~~~
Usage:
python glue_def_extract.py -d "<insert database name from Glue catalog>" -f "output.json"

~~~
6. Configure the source endpoint in AWS DMS using this JSON document


## Limitations
* AWS DMS can also create tables in the target database, however the AWS Glue catalog does not detect lengths of varchar columns which is required by AWS DMS to create tables.  Setting a default length with a high value in the python script will ensure data loads succeed
* Support for data types is limited to data types allowed by the AWS Glue catalog


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


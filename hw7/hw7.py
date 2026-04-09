import argparse
import logging
import re

import apache_beam as beam
from apache_beam.io import ReadAllFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

def get_link_destinations(line):
  links = re.findall(r'<a href="(\d+).html"> This is a link </a>', line)
  result = []
  for link in links:
    start = link.find('<a href=\"')
    end = link.find('.html\"> This is a link </a>')
    if start != -1 and end != -1:
        link_to = int(link[start+9:end])
        result.append(link_to)
  return result

def main(argv=None, save_main_session=True):
  """Main entry point; defines and runs the wordcount pipeline."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      default='gs://alhoe528hw2/files/*.txt',
      help='Input file to process.')
  parser.add_argument(
      '--output',
      dest='output',
      # CHANGE 1/6: (OPTIONAL) The Google Cloud Storage path is required
      # for outputting the results.
      default='gs://alhoe528hw2/hw7/output/*.txt',
      help='Output file to write results to.')

  # If you use DataflowRunner, below options can be passed:
  #   CHANGE 2/6: (OPTIONAL) Change this to DataflowRunner to
  #   run your pipeline on the Google Cloud Dataflow Service.
  #   '--runner=DirectRunner',
  #   CHANGE 3/6: (OPTIONAL) Your project ID is required in order to
  #   run your pipeline on the Google Cloud Dataflow Service.
  #   '--project=SET_YOUR_PROJECT_ID_HERE',
  #   CHANGE 4/6: (OPTIONAL) The Google Cloud region (e.g. us-central1)
  #   is required in order to run your pipeline on the Google Cloud
  #   Dataflow Service.
  #   '--region=SET_REGION_HERE',
  #   CHANGE 5/6: Your Google Cloud Storage path is required for staging local
  #   files.
  #   '--staging_location=gs://YOUR_BUCKET_NAME/AND_STAGING_DIRECTORY',
  #   CHANGE 6/6: Your Google Cloud Storage path is required for temporary
  #   files.
  #   '--temp_location=gs://YOUR_BUCKET_NAME/AND_TEMP_DIRECTORY',
  #   '--job_name=your-wordcount-job',
  known_args, pipeline_args = parser.parse_known_args(argv)

  options = PipelineOptions(
    runner='DataflowRunner',
    project='bucsece528',
    region='us-south1',
    temp_location='gs://alhoe528hw2/temp',
    auto_unique_labels=True
)

  # We use the save_main_session option because one or more DoFn's in this
  # workflow rely on global context (e.g., a module imported at module level).
  #pipeline_options = PipelineOptions(pipeline_args)
  options.view_as(SetupOptions).save_main_session = save_main_session
  with beam.Pipeline(options=options) as p:

    lines = p | beam.Create(['gs://alhoe528hw2/files/*42.html']) | ReadAllFromText(with_filename=True)

    outgoing = (
        lines
           | 'Links' >> (
            beam.Map(
                lambda x: (x[0], len(re.findall(r'<a HREF="(\d+).html"> This is a link </a>', x[1])))))
            | 'SumByFile' >> beam.CombinePerKey(sum)
            | 'Top5outgoing' >> beam.combiners.Top.Of(5,key=lambda x: x[1])
            )
    # Format the counts into a PCollection of strings.
    #def format_result(word_count):
    #  (word, count) = word_count
    #  return '%s: %s' % (word, count)

    #output = counts | 'Format' >> beam.Map(format_result)

    # Write the output using a "Write" transform that has side effects.
    # pylint: disable=expression-not-assigned
    outgoing | WriteToText('gs://alhoe528hw2/hw7/outgoing.txt')
    #incoming | WriteToText('gs://alhoe528hw2/hw7/incoming.txt')


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  main()
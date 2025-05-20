const { DocumentAnalyzer } = require('../services/aiAgents/documentAnalyzer');
const cron = require('node-cron');

// Initialize the document analyzer
const analyzer = new DocumentAnalyzer();

// Set up cron job to run every hour
const schedule = '0 * * * *'; // Every hour

// Create the monitor function
cron.schedule(schedule, async () => {
  try {
    console.log('Starting GovInfo monitoring...');
    await analyzer.monitorGovInfo();
    console.log('GovInfo monitoring completed successfully');
  } catch (error) {
    console.error('Error in GovInfo monitoring:', error);
  }
});

// Export for testing
module.exports = {
  startMonitor: () => {
    console.log('Starting GovInfo monitor...');
    cron.schedule(schedule, async () => {
      try {
        console.log('Starting GovInfo monitoring...');
        await analyzer.monitorGovInfo();
        console.log('GovInfo monitoring completed successfully');
      } catch (error) {
        console.error('Error in GovInfo monitoring:', error);
      }
    });
  }
};

"""
Checklist Reporter - Generates CSV reports from pytest results.

This module tracks test results and generates a CSV report matching
the format of the Testing_Checklists.csv file.
"""
import csv
import os
from datetime import datetime


class ChecklistReporter:
    """
    Track and report test results for checklist items.
    
    This class collects test results during pytest execution and generates
    a CSV report showing which checklist items passed or failed.
    """
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def add_result(self, item_number, module, function, status, duration, error=None):
        """
        Add a test result.
        
        Args:
            item_number: Checklist item number (1-211)
            module: Module name (e.g., "Database", "Backend API")
            function: Function name being tested
            status: "PASS", "FAIL", or "ERROR"
            duration: Test execution time in seconds
            error: Error message if failed
        """
        self.results.append({
            'item_number': item_number,
            'module': module,
            'function': function,
            'status': status,
            'duration': duration,
            'error': error or ''
        })
    
    def generate_csv(self, filepath='test_results.csv'):
        """
        Generate CSV report matching checklist format.
        
        Args:
            filepath: Output file path
            
        Returns:
            str: Path to generated file
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header row matching checklist format
            writer.writerow([
                'Item #',
                'Module',
                'Function',
                'Input',
                'Expected Result',
                'Output',
                'Automated Test Result',
                'Duration',
                'Error/Notes'
            ])
            
            # Write results
            for r in self.results:
                writer.writerow([
                    r['item_number'],
                    r['module'],
                    r['function'],
                    '',  # Input (not tracked)
                    '',  # Expected (not tracked)
                    '',  # Output (not tracked)
                    r['status'],
                    f"{r['duration']:.3f}s",
                    r['error']
                ])
        
        return filepath
    
    def print_summary(self):
        """Print test summary to console."""
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        errors = len([r for r in self.results if r['status'] == 'ERROR'])
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("AIEAT CHECKLIST TEST RESULTS")
        print("="*80)
        print(f"Total Tests:     {total}")
        print(f"Passed:          {passed} ({passed/total*100:.1f}%)")
        print(f"Failed:          {failed}")
        print(f"Errors:          {errors}")
        print(f"Execution Time:  {duration:.2f}s")
        print("="*80)
        
        if failed > 0 or errors > 0:
            print("\nFailed Tests:")
            for r in self.results:
                if r['status'] in ['FAIL', 'ERROR']:
                    print(f"  Item {r['item_number']:3d} [{r['module']:15s}] {r['function']:40s}")
        
        print(f"\nReport saved to: {os.path.abspath('test_results.csv')}")


# Global reporter instance
reporter = ChecklistReporter()


# Pytest hooks for integration
def pytest_configure(config):
    """Configure pytest with our reporter."""
    config._checklist_reporter = reporter


def pytest_runtest_logreport(report):
    """Hook to capture test results."""
    if report.when == 'call':
        # Extract checklist info from user_properties
        props = dict(report.user_properties)
        
        item_number = props.get('item_number', 'N/A')
        module = props.get('module', 'Unknown')
        function = props.get('function', report.nodeid.split('::')[-1])
        
        if report.passed:
            status = 'PASS'
        elif report.failed:
            status = 'FAIL'
        elif report.skipped:
            status = 'SKIP'
        else:
            status = 'ERROR'
        
        reporter.add_result(
            item_number=item_number,
            module=module,
            function=function,
            status=status,
            duration=report.duration,
            error=str(report.longrepr) if report.failed else None
        )
    elif report.when == 'setup' and report.skipped:
        # Handle tests skipped via @pytest.mark.skip
        props = dict(report.user_properties) if report.user_properties else {}
        reporter.add_result(
            item_number=props.get('item_number', 'N/A'),
            module=props.get('module', 'Unknown'),
            function=props.get('function', report.nodeid.split('::')[-1]),
            status='SKIP',
            duration=0,
            error=str(report.longrepr) if report.longrepr else 'Skipped'
        )


def pytest_sessionfinish(session, exitstatus):
    """Generate report at end of test session."""
    reporter.generate_csv()
    reporter.print_summary()

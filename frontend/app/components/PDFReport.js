import React from 'react';
import { Document, Page, Text, View, StyleSheet, PDFDownloadLink } from '@react-pdf/renderer';

// Create styles - using default fonts that work reliably
const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 12,
    fontFamily: 'Helvetica',  // Using built-in font
  },
  header: {
    marginBottom: 30,
    borderBottomWidth: 2,
    borderBottomColor: '#3B82F6',
    borderBottomStyle: 'solid',
    paddingBottom: 15
  },
  logo: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1E40AF',
    marginBottom: 5
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#111827'
  },
  subtitle: {
    fontSize: 11,
    color: '#6B7280'
  },
  section: {
    marginBottom: 25
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E40AF',
    marginBottom: 10,
    paddingBottom: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    borderBottomStyle: 'solid'
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 8
  },
  label: {
    width: 140,
    fontWeight: 'bold',
    color: '#4B5563',
    fontSize: 12
  },
  value: {
    flex: 1,
    color: '#111827',
    fontSize: 12
  },
  trialCard: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderStyle: 'solid',
    borderRadius: 5,
    padding: 15,
    marginBottom: 15,
    backgroundColor: '#F9FAFB'
  },
  trialTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#111827'
  },
  trialId: {
    fontSize: 10,
    color: '#6B7280',
    marginBottom: 8
  },
  statusContainer: {
    flexDirection: 'row',
    marginBottom: 10
  },
  statusBadge: {
    fontSize: 10,
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 3,
  },
  eligible: {
    backgroundColor: '#D1FAE5',
    color: '#065F46'
  },
  notEligible: {
    backgroundColor: '#FEE2E2',
    color: '#991B1B'
  },
  needsReview: {
    backgroundColor: '#FEF3C7',
    color: '#92400E'
  },
  explanation: {
    fontSize: 11,
    color: '#374151',
    lineHeight: 1.6
  },
  footer: {
    position: 'absolute',
    bottom: 40,
    left: 40,
    right: 40,
    fontSize: 9,
    color: '#6B7280',
    textAlign: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    borderTopStyle: 'solid',
    paddingTop: 10
  },
  summaryBox: {
    backgroundColor: '#F3F4F6',
    padding: 20,
    borderRadius: 5,
    marginTop: 20,
    marginBottom: 20
  },
  summaryTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#111827'
  },
  summaryStats: {
    flexDirection: 'row',
    justifyContent: 'space-around'
  },
  stat: {
    alignItems: 'center'
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1E40AF'
  },
  statLabel: {
    fontSize: 10,
    color: '#6B7280',
    marginTop: 5
  },
  pageNumber: {
    position: 'absolute',
    fontSize: 10,
    bottom: 20,
    left: 0,
    right: 0,
    textAlign: 'center',
    color: '#9CA3AF'
  }
});

const TrialReport = ({ patient, results }) => {
  const date = new Date().toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  const eligibleCount = results.matches?.filter(m => m.status === 'ELIGIBLE').length || 0;
  const notEligibleCount = results.matches?.filter(m => m.status === 'NOT_ELIGIBLE').length || 0;
  const reviewCount = results.matches?.filter(m => m.status === 'NEEDS_REVIEW').length || 0;
  const totalCount = results.matches?.length || 0;

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>ClinicalMatch AI</Text>
          <Text style={styles.title}>Clinical Trial Matching Report</Text>
          <Text style={styles.subtitle}>Generated on {date}</Text>
        </View>

        {/* Patient Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Patient Information</Text>
          
          <View style={styles.infoRow}>
            <Text style={styles.label}>Age:</Text>
            <Text style={styles.value}>{patient.age} years</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.label}>Gender:</Text>
            <Text style={styles.value}>{patient.gender}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.label}>Conditions:</Text>
            <Text style={styles.value}>{patient.conditions || 'Not specified'}</Text>
          </View>
          
          {patient.medications && (
            <View style={styles.infoRow}>
              <Text style={styles.label}>Medications:</Text>
              <Text style={styles.value}>{patient.medications}</Text>
            </View>
          )}
          
          {patient.biomarkers && (
            <View style={styles.infoRow}>
              <Text style={styles.label}>Biomarkers:</Text>
              <Text style={styles.value}>{patient.biomarkers}</Text>
            </View>
          )}
        </View>

        {/* Summary Statistics */}
        <View style={styles.summaryBox}>
          <Text style={styles.summaryTitle}>Analysis Summary</Text>
          <View style={styles.summaryStats}>
            <View style={styles.stat}>
              <Text style={styles.statNumber}>{totalCount}</Text>
              <Text style={styles.statLabel}>Trials Analyzed</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statNumber}>{eligibleCount}</Text>
              <Text style={styles.statLabel}>Eligible</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statNumber}>{reviewCount}</Text>
              <Text style={styles.statLabel}>Need Review</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statNumber}>{notEligibleCount}</Text>
              <Text style={styles.statLabel}>Not Eligible</Text>
            </View>
          </View>
        </View>

        {/* Trial Results */}
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>Trial Match Results</Text>
            {results.matches && results.matches.length > 0 ? (
                results.matches.slice(0, 5).map((match, idx) => (
                <View key={idx} style={styles.trialCard}>
                    <Text style={styles.trialTitle}>
                    {match.title || 'Clinical Trial'}
                    </Text>
                    <Text style={styles.trialId}>
                    NCT ID: {match.nct_id || 'Not specified'}
                    </Text>
                    
                    <View style={styles.statusContainer}>
                    <View style={[
                        styles.statusBadge,
                        match.status === 'ELIGIBLE' ? styles.eligible :
                        match.status === 'NOT_ELIGIBLE' ? styles.notEligible :
                        styles.needsReview
                    ]}>
                        <Text style={{
                        fontSize: 10,
                        color: match.status === 'ELIGIBLE' ? '#065F46' :
                                match.status === 'NOT_ELIGIBLE' ? '#991B1B' : '#92400E'
                        }}>
                        {match.status?.replace('_', ' ') || 'UNKNOWN'}
                        </Text>
                    </View>
                    </View>
                    
                    <Text style={styles.explanation}>
                    Analysis: {match.explanation ? 
                        `Based on the patient's ${patient.conditions || 'condition'} and biomarkers, this trial appears to be a ${match.status === 'ELIGIBLE' ? 'good' : 'potential'} match. ${match.explanation}`.substring(0, 300) :
                        'Detailed eligibility analysis requires consultation with the trial coordinator.'}
                    </Text>
                </View>
                ))
            ) : (
                <Text style={styles.explanation}>No trials analyzed.</Text>
            )}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text>
            This report is for informational purposes only and should not replace professional medical advice.
          </Text>
          <Text style={{ marginTop: 5 }}>
            Please consult with your healthcare provider before making any medical decisions.
          </Text>
        </View>

        {/* Page Number */}
        <Text style={styles.pageNumber}>Page 1 of 1</Text>
      </Page>
    </Document>
  );
};

export default function PDFReportButton({ patient, results }) {
  if (!results || !results.matches) return null;

  return (
    <PDFDownloadLink
      document={<TrialReport patient={patient} results={results} />}
      fileName={`clinical-trial-report-${new Date().getTime()}.pdf`}
      className="flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg hover:shadow-lg transition"
    >
      {({ loading }) => (
        <>
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{loading ? 'Generating PDF...' : 'Download PDF Report'}</span>
        </>
      )}
    </PDFDownloadLink>
  );
}
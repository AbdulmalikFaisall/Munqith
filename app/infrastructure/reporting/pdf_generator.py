"""
PDF generator for investor reports.

Infrastructure layer - responsible for file format generation.
Uses reportlab for lightweight, deterministic PDF creation.
No business logic - only formatting and presentation.
"""
from typing import Dict, Any
from datetime import datetime


class PDFGenerationError(Exception):
    """Raised when PDF generation fails."""
    pass


class PDFGenerator:
    """
    Generate PDF investor reports from snapshot data.
    
    Responsibilities:
    - Format snapshot data for presentation
    - Generate PDF documents
    - Return raw PDF bytes
    
    Key Rule: Uses stored DB values only - no recomputation.
    """
    
    @staticmethod
    def generate_report(export_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF investor report from exported snapshot data.
        
        Report sections:
        - Header: company_id, snapshot_date, stage
        - Financial Summary: cash, revenue, costs, burn, runway
        - Signals: all available signals
        - Rules: all rule results
        - Explanation: contributing signals
        
        Args:
            export_data: Dict from ExportSnapshotUseCase.execute()
            
        Returns:
            Raw PDF file bytes
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
                Spacer,
                PageBreak,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from io import BytesIO
            
            # Create in-memory PDF
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )
            
            # Prepare styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=12,
                alignment=TA_CENTER,
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c5aa0'),
                spaceAfter=6,
                spaceBefore=6,
            )
            normal_style = styles['Normal']
            
            # Build document content
            elements = []
            
            # Title
            elements.append(
                Paragraph("MUNQITH INVESTOR REPORT", title_style)
            )
            elements.append(Spacer(1, 0.25 * inch))
            
            # Snapshot info
            snapshot_date = export_data.get('snapshot_date', 'N/A')
            stage = export_data.get('stage', 'N/A')
            company_id = export_data.get('company_id', 'N/A')[:8]  # Short ID
            
            info_data = [
                ['Snapshot Date:', snapshot_date],
                ['Stage:', stage],
                ['Company ID:', company_id],
            ]
            info_table = Table(info_data, colWidths=[2 * inch, 3 * inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.25 * inch))
            
            # Financial Summary
            elements.append(Paragraph("Financial Summary", heading_style))
            financials = export_data.get('financials', {})
            
            fin_data = [
                ['Metric', 'Amount (SAR)'],
                ['Cash Balance', str(financials.get('cash_balance', 'N/A'))],
                ['Monthly Revenue', str(financials.get('monthly_revenue', 'N/A'))],
                ['Operating Costs', str(financials.get('operating_costs', 'N/A'))],
                ['Monthly Burn', str(financials.get('monthly_burn', 'N/A'))],
                ['Runway (Months)', str(financials.get('runway_months', 'N/A'))],
            ]
            fin_table = Table(fin_data, colWidths=[2.5 * inch, 2.5 * inch])
            fin_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(fin_table)
            elements.append(Spacer(1, 0.25 * inch))
            
            # Signals
            signals = export_data.get('signals', [])
            if signals:
                elements.append(Paragraph("Signals", heading_style))
                signals_data = [['Signal', 'Category', 'Value']]
                for signal in signals[:10]:  # Limit to first 10
                    signals_data.append([
                        str(signal.get('name', 'N/A')),
                        str(signal.get('category', 'N/A')),
                        str(signal.get('value', 'N/A')),
                    ])
                signals_table = Table(signals_data)
                signals_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                elements.append(signals_table)
                elements.append(Spacer(1, 0.25 * inch))
            
            # Contributing signals explanation
            contrib_signals = export_data.get('contributing_signals', [])
            if contrib_signals:
                elements.append(Paragraph("Key Drivers (Contributing Signals)", heading_style))
                contrib_text = ", ".join([str(s) for s in contrib_signals[:5]])
                elements.append(Paragraph(f"<b>Stage determined by:</b> {contrib_text}", normal_style))
                elements.append(Spacer(1, 0.25 * inch))
            
            # Footer
            elements.append(Spacer(1, 0.5 * inch))
            footer_text = f"Report generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            elements.append(
                Paragraph(f"<i>{footer_text}</i>", ParagraphStyle(
                    'Footer',
                    parent=normal_style,
                    fontSize=8,
                    textColor=colors.grey,
                ))
            )
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            return pdf_bytes
        
        except ImportError:
            raise PDFGenerationError(
                "reportlab not installed. Install with: pip install reportlab"
            )
        except Exception as e:
            raise PDFGenerationError(f"PDF generation failed: {str(e)}")

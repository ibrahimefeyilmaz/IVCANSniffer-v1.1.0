import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtCore import QTimer

class ArtificialHorizon(QWidget):
    """A custom PyQt6 widget that visualizes aircraft attitude.

    Displays a dynamic artificial horizon indicating pitch and roll angles
    using standard aviation colors (blue sky, brown ground), a dynamic pitch 
    ladder, and a static aircraft reference icon.
    """

    def __init__(self, parent=None):
        """Initializes the Artificial Horizon widget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.pitch = 0.0  
        self.roll = 0.0   
        self.setMinimumSize(200, 200)

    def set_artificial_horizon(self, attitude_data):
        """Updates the pitch and roll values and triggers a UI repaint.

        Extracts the pitch and roll from a single packed data structure 
        to maintain compatibility with the single-argument routing system.

        Args:
            attitude_data (tuple or list): A sequence containing exactly two float 
                values representing (pitch, roll) in degrees.
        """
        # Gelen verinin beklediğimiz formatta (tuple/list) olup olmadığını kontrol et
        if isinstance(attitude_data, (tuple, list)) and len(attitude_data) == 2:
            self.pitch = attitude_data[0]
            self.roll = attitude_data[1]
            self.update()
        else:
            # Yanlış formatta veri gelirse (örneğin sistem 0.0 gibi tek bir float gönderirse)
            # varsayılan değerlere çekebilir veya pas geçebilirsin.
            pass

    def paintEvent(self, event):
        """Handles the rendering of the artificial horizon graphics.

        Draws the rotating sky/ground background, translates the pitch ladder, 
        and superimposes the static aircraft reference frame on top.

        Args:
            event (QPaintEvent): The paint event parameters provided by PyQt.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 

        width = self.width()
        height = self.height()
        
        side = min(width, height)
        radius = side / 2.0

        painter.translate(width / 2.0, height / 2.0)

        clip_path = QPainterPath()
        clip_path.addEllipse(QPointF(0, 0), radius, radius)
        painter.setClipPath(clip_path)

        # -------------------------------------------------------------------
        # HAREKETLİ KATMAN
        # -------------------------------------------------------------------
        painter.save()
        painter.rotate(-self.roll)
        
        pitch_factor = radius / 45.0
        painter.translate(0, self.pitch * pitch_factor)

        bg_size = int(side * 2)

        # Gökyüzü (Mavi)
        painter.setPen(Qt.PenStyle.NoPen) 
        painter.setBrush(QColor(0, 114, 198))
        painter.drawRect(-bg_size, -bg_size, bg_size * 2, bg_size)

        # Yer (Kahverengi)
        painter.setBrush(QColor(122, 75, 41))
        painter.drawRect(-bg_size, 0, bg_size * 2, bg_size)

        # Ufuk Çizgisi
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
        painter.drawLine(int(-bg_size), 0, int(bg_size), 0) 

        # -------------------------------------------------------------------
        # PITCH KADEME ÇİZGİLERİ VE SAYISAL DEĞERLER (YENİ EKLENEN KISIM)
        # -------------------------------------------------------------------
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        
        # Dinamik font ayarı
        font = painter.font()
        font.setPixelSize(int(radius * 0.12)) # Font büyüklüğünü widget'a göre ayarla
        font.setBold(True)
        painter.setFont(font)

        for i in range(-30, 40, 10):
            if i == 0: continue 
            y_pos = int(-i * pitch_factor)
            line_length = int(radius * 0.3)
            
            # Kademe çizgisini çiz
            painter.drawLine(-line_length, y_pos, line_length, y_pos)

            # Sayısal değer (Havacılık standardı olarak genelde mutlak değer kullanılır: 10, 20)
            text = str(abs(i))
            
            # Yazıların hizalanacağı görünmez kutuların boyutları
            rect_width = int(radius * 0.4)
            rect_height = int(radius * 0.2)
            margin = 5 # Çizgiden kaç piksel uzak olacağı
            
            # Sol Taraf Metni (Sağa yaslı)
            left_rect = QRectF(-line_length - rect_width - margin, y_pos - rect_height / 2, rect_width, rect_height)
            painter.drawText(left_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, text)
            
            # Sağ Taraf Metni (Sola yaslı)
            right_rect = QRectF(line_length + margin, y_pos - rect_height / 2, rect_width, rect_height)
            painter.drawText(right_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)

        painter.restore()

        # -------------------------------------------------------------------
        # SABİT KATMAN (Uçak İkonu)
        # -------------------------------------------------------------------
        
        # Dış Çerçeve
        painter.setPen(QPen(QColor(50, 50, 50), 6))
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.drawEllipse(QPointF(0, 0), radius - 3, radius - 3)

        # Uçak İkonu
        pen = QPen(QColor(255, 140, 0), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        painter.drawPoint(0, 0)
        
        painter.drawLine(QPointF(-radius * 0.6, 0), QPointF(-radius * 0.15, 0))
        painter.drawLine(QPointF(-radius * 0.15, 0), QPointF(-radius * 0.15, radius * 0.1))
        
        painter.drawLine(QPointF(radius * 0.6, 0), QPointF(radius * 0.15, 0))
        painter.drawLine(QPointF(radius * 0.15, 0), QPointF(radius * 0.15, radius * 0.1))
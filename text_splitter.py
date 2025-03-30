class TextSplitter:
    def __init__(self, max_words=4000):
        self.max_words = max_words
        
    def split_document(self, text):
        # Split the text by paragraphs (double newlines)
        paragraphs = text.split('\n\n')
        
        segments = []
        current_segment = []
        current_word_count = 0
        
        for paragraph in paragraphs:
            # Count words in the current paragraph
            paragraph_words = len(paragraph.split())
            
            # If adding this paragraph exceeds max_words and we already have content,
            # finish the current segment and start a new one
            if current_word_count + paragraph_words > self.max_words and current_segment:
                segments.append('\n\n'.join(current_segment) + '\n\n')
                current_segment = []
                current_word_count = 0
            
            # Handle paragraphs that are larger than max_words on their own
            if paragraph_words > self.max_words:
                # If we have content in the current segment, add it as a segment
                if current_segment:
                    segments.append('\n\n'.join(current_segment) + '\n\n')
                    current_segment = []
                    current_word_count = 0
                
                # Split the large paragraph into words
                words = paragraph.split()
                temp_paragraph = []
                temp_word_count = 0
                
                for word in words:
                    if temp_word_count + 1 <= self.max_words:
                        temp_paragraph.append(word)
                        temp_word_count += 1
                    else:
                        segments.append(' '.join(temp_paragraph) + '\n\n')
                        temp_paragraph = [word]
                        temp_word_count = 1
                
                if temp_paragraph:
                    current_segment.append(' '.join(temp_paragraph))
                    current_word_count = temp_word_count
            else:
                # Add paragraph to the current segment
                current_segment.append(paragraph)
                current_word_count += paragraph_words
        
        # Add the last segment if it has content
        if current_segment:
            segments.append('\n\n'.join(current_segment) + '\n\n')
        
        return segments

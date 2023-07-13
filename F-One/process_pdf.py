import pdfplumber as pdfplumber
import os
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
import tiktoken


from config import path_directory 



def check_equal(list1, val):
    return(all(x == val for x in list1))


def check_smaller(list1, val):
    return(all(x < val for x in list1))


def check_between_equal(list1, val1, val2):
    return(all(((x >= val1) and (x <= val2)) for x in list1))


def create_final_docs(path_directory):
    document_files = os.listdir(path_directory)
    list_n = [(0, 0, 595.08, 760), (0, 0, 595.32, 780), (0, 0, 595.32, 760)]
    documents = []
    total_words = 0

    for file in document_files:
        if os.path.isfile(os.path.join(path_directory + '/', file)):
            if file == "fia_2023_formula_1_sporting_regulations_-_issue_4_-_2023-02-22.pdf":
                n = list_n[0]
            elif file == "fia_2023_formula_1_technical_regulations_-_issue_5_-_2023-02-22.pdf":
                n = list_n[1]
            elif file == "fia_formula_1_financial_regulations_iss.14_.pdf":
                n = list_n[2]
            else:
                raise TypeError("ATTENTION: There is a pdf file non considered")
            

            with pdfplumber.open(path_directory + '/' + file) as pdf:
                source_pdf = {"source": '{}'.format(file)}
                print("\n\n" , file)
                num_pages = len(pdf.pages)
                print("Total page document: {}".format(num_pages))

                previous_dict = []
                previous_final_dict = []


                for i in range(num_pages):
                    print("Page Number: {}".format(i+1))
                    page_obj = pdf.pages[i]
                    page_obj = page_obj.crop(n, relative=False, strict=True)
                    lines = page_obj.extract_text_lines(layout=False, 
                                                        strip=True, 
                                                        return_chars=True,
                                                        )
                    ####
                    print('Number of lines: ', len(lines))
                    dict = {}
                    final_dict = {}
                    content = ''
                    sub_paragraph = ''
                    paragraph = ''
                    chapter = ''
                    iter = -1
                    iter_list = []
            
                    for l in lines:
                        iter += 1
                        size_words_line = []
                        for w in l['chars']:
                            size_words_line.append(w['size'])
                        stamp_content = check_smaller(size_words_line, 11.5)
                        stamp_sub_paragraph = check_between_equal(size_words_line, 11.5, 12.5)
                        stamp_paragraph = check_between_equal(size_words_line, 13.5, 14.5)
                        stamp_chapter = check_between_equal(size_words_line, 15.5, 16.5)
                        if stamp_content == True:
                            iter_list.append('A')
                            content += l['text'] + '\n'
                        elif stamp_sub_paragraph == True:
                            iter_list.append('B')
                            sub_paragraph += l['text'] + '\n'
                        elif stamp_paragraph == True:
                            iter_list.append('C')
                            paragraph += l['text'] + '\n'
                        elif stamp_chapter == True:
                            iter_list.append('D')
                            chapter += l['text'] + '\n'
                        else:
                            iter_list.append('E')

                        if iter > 0:

                            if ((iter_list[iter-1]=='D') and (iter_list[iter] != iter_list[iter-1])):
                                dict['Chapter'] = chapter
                                chapter = ''
                                if dict.get('Content') is not None:
                                    del dict['Content']
                                if dict.get('Sub Paragraph') is not None:
                                    del dict['Sub Paragraph']
                                if dict.get('Paragraph') is not None:
                                    del dict['Paragraph']
                            else:
                                pass

                            if ((iter_list[iter-1]=='C') and (iter_list[iter] != iter_list[iter-1])):
                                dict['Paragraph'] = paragraph
                                paragraph = ''
                                if dict.get('Content') is not None:
                                    del dict['Content']
                                if dict.get('Sub Paragraph') is not None:
                                    del dict['Sub Paragraph']
                            else:
                                pass

                            if ((iter_list[iter-1]=='B') and (iter_list[iter] != iter_list[iter-1])):
                                dict['Sub Paragraph'] = sub_paragraph
                                sub_paragraph = ''
                                if dict.get('Content') is not None:
                                    del dict['Content']
                            else:
                                pass


                            if ((iter_list[iter-1]=='A') and (iter_list[iter] != iter_list[iter-1]) or (iter == len(lines)-1)) :
                                dict['Content'] = content
                                dict['Page Number'] = i + 1
                                content = ''


                                # Conditions for handling information when moving from one page to another
                                if (dict.get('Chapter') is not None) and (dict.get('Paragraph') is None) and (dict.get('Sub Paragraph') is None):          # 1 0 0
                                    dict['Paragraph'] = ''
                                    dict['Sub Paragraph'] = ''

                                elif (dict.get('Chapter') is not None) and (dict.get('Paragraph') is not None) and (dict.get('Sub Paragraph') is None):    # 1 1 0
                                    dict['Sub Paragraph'] = ''

                                elif (dict.get('Chapter') is not None) and (dict.get('Paragraph') is None) and (dict.get('Sub Paragraph') is not None):    # 1 0 1
                                    dict['Paragraph'] = ''

                                elif (dict.get('Chapter') is None) and (dict.get('Paragraph') is None) and (dict.get('Sub Paragraph') is None):            # 0 0 0
                                    try:
                                        dict['Chapter'] = previous_dict[0]['Chapter']
                                    except:
                                        dict['Chapter'] = ''
                                    try:
                                        dict['Paragraph'] = previous_dict[0]['Paragraph']
                                    except:
                                        dict['Paragraph'] = ''

                                    try:
                                        dict['Sub Paragraph'] = previous_dict[0]['Sub Paragraph']
                                    except:
                                        dict['Sub Paragraph'] = ''
                                
                                elif (dict.get('Chapter') is None) and (dict.get('Paragraph') is not None) and (dict.get('Sub Paragraph') is not None):    # 0 1 1
                                    try:
                                        dict['Chapter'] = previous_dict[0]['Chapter']
                                    except:
                                        dict['Chapter'] = ''
                                
                                elif (dict.get('Chapter') is None) and (dict.get('Paragraph') is None) and (dict.get('Sub Paragraph') is not None):        # 0 0 1
                                    try:
                                        dict['Chapter'] = previous_dict[0]['Chapter']
                                    except:
                                        dict['Chapter'] = ''
                                    try:
                                        dict['Paragraph'] = previous_dict[0]['Paragraph']
                                    except:
                                        dict['Paragraph'] = ''
                                
                                elif (dict.get('Chapter') is None) and (dict.get('Paragraph') is not None) and (dict.get('Sub Paragraph') is None):        # 0 1 0
                                    try:
                                        dict['Chapter'] = previous_dict[0]['Chapter']
                                    except:
                                        dict['Chapter'] = ''
                                    
                                    dict['Sub Paragraph'] = ''
                                
                                else:
                                    pass

                            
                                previous_dict = []
                                previous_dict.append(dict)


                                keyorder = ['Page Number', 'Chapter', 'Paragraph', 'Sub Paragraph', 'Content']
                                final_dict = {k: dict[k] for k in keyorder if k in dict}

                                previous_final_dict = []
                                previous_final_dict.append(final_dict)

                                total_words+=len(final_dict['Content'].split())

                                
                                meta_dict = {'Page Number': final_dict['Page Number'], 'Chapter': final_dict['Chapter'], 'Paragraph': final_dict['Paragraph'], 'Sub Paragraph': final_dict['Sub Paragraph']}
                                metadata_all = source_pdf | meta_dict 
                                doc = Document( page_content = final_dict['Content'],
                                                metadata = metadata_all
                                                )
                                
                                documents.append(doc)
                            else:
                                pass
                            

                            if (iter == len(lines)-1):
                                if iter_list[iter] == 'B':
                                    dict['Sub Paragraph'] = sub_paragraph
                                    dict['Page Number'] = i + 1
                                    sub_paragraph = ''
                                    if dict.get('Content') is not None:
                                        del dict['Content']

                                    previous_dict = []
                                    previous_dict.append(dict)

                                elif iter_list[iter] == 'C':
                                    dict['Paragraph'] = paragraph
                                    dict['Page Number'] = i + 1
                                    paragraph = ''
                                    if dict.get('Sub Paragraph') is not None:
                                        del dict['Sub Paragraph']
                                    if dict.get('Content') is not None:
                                        del dict['Content']

                                    previous_dict = []
                                    previous_dict.append(dict)

                                elif iter_list[iter] == 'D':
                                    dict['Chapter'] = chapter
                                    dict['Page Number'] = i + 1
                                    chapter = ''
                                    if dict.get('Content') is not None:
                                        del dict['Content']
                                    if dict.get('Sub Paragraph') is not None:
                                        del dict['Sub Paragraph']
                                    if dict.get('Paragraph') is not None:
                                        del dict['Paragraph']
                                    
                                    previous_dict = []
                                    previous_dict.append(dict)

                                else:
                                    pass
                

    print('\n\n Total Words: ', total_words)
    print('Total documents: ', len(documents))
    return documents




def split_final_docs(documents):
    text_splitter = CharacterTextSplitter(
            separator='\n', 
            chunk_size = 800,
            chunk_overlap = 10
       )

    split_docs = text_splitter.split_documents(documents)
    return split_docs



def embedding_cost_estimation(split_docs):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

    total_word_count = sum(len(doc.page_content.split()) for doc in split_docs)
    total_token_count = sum(len(enc.encode(doc.page_content)) for doc in split_docs)

    return print(f"\nTotal word count: {total_word_count} \n" 
                 f"\nEstimated tokens: {total_token_count} \n" 
                 f"\nEstimated cost of embedding: ${total_token_count * 0.0004 / 1000} \n")


def get_final_docs(path_directory):
    documents = create_final_docs(path_directory)
    split_docs = split_final_docs(documents) 
    return documents, split_docs


if __name__ == "__main__":

    _ ,split_docs = get_final_docs(path_directory)
    
    embedding_cost_estimation(split_docs)